from typing import TypeVar, Generic, Optional, List, Type, Dict, Any, Union
from pydantic import BaseModel
import pandas as pd
import csv
import os
import configparser

T = TypeVar("T", bound=BaseModel)


class CSVVectorizedStorage(Generic[T]):
    """
    Generic CSV storage for schema objects or DataFrames, with support for vectorized sharding.

    Design idea:
    -----------------
    - This class allows storing historical data where each row represents a schema object (T)
      or a DataFrame row.
    - Vectorization: Users can specify `vectorize_by` fields. Data will be automatically
      split into multiple CSV files, one per unique combination of values in these fields.
    - File naming: Files are named as <prefix>_field1_value1_field2_value2.csv.
    - Reading supports filters: you can selectively load only the files corresponding to
      specific vectorized values.
    - This design separates **schema concerns** (what fields exist) from **storage concerns**
      (CSV and file organization). It also allows efficient selective reading of vectorized data.

    Features:
    - Works with Pydantic BaseModel objects or pandas DataFrames.
    - Supports any number of vectorization fields.
    - Can convert loaded objects into a DataFrame for analytics.
    """

    def __init__(self, schema_class: Type[T],
                       vectorize_by: Optional[List[str]] = None,
                       csv_path: str = "CsvPath",
                       csv_filename_prefix: str = "CsvPrefix"):
        """
        Initialize the CSV vectorized storage.

        :Parameters:
        -----------
        schema_class : Type[T]
            The Pydantic model class representing the schema (T) of each row.

        vectorize_by : Optional[List[str]], default=None
            List of field names to shard the data by. Each unique combination of
            these field values will be written to a separate CSV file.

        config_section : str, default="CsvStorage"
            The section in the configuration file (INI) where the storage settings
            are located.

        key_path : str, default="CsvPath"
            The key in the config section that specifies the base directory for CSV storage.

        key_filename_prefix : str, default="CsvPrefix"
            The key in the config section that specifies the prefix to use for all CSV filenames.
        """
        self.schema_class = schema_class
        self.vectorize_by = vectorize_by or []
        self.csv_path = csv_path
        self.csv_filename_prefix = csv_filename_prefix


    def _get_file_path(self, row: Dict[str, Any]) -> str:
        """
        Generate the file path for a row based on vectorize_by fields.

        :param row: Dictionary representing the row (object or DataFrame row).
        :return: Full path to the CSV file where this row should be stored.
        """
        parts = [f"{f}_{row[f]}" for f in self.vectorize_by]
        filename = "_".join([self.csv_filename_prefix] + parts) + ".csv"
        return os.path.join(self.csv_path, filename)


    def write(self, data: Union[List[T], pd.DataFrame], **kwargs) -> None:
        """
        Write data to CSV files, optionally vectorized by fields.

        :param data: List of schema objects (T) or pandas DataFrame.
        """
        if not self.base_path:
            raise ValueError("Storage not configured. Call configure_from_config first.")
        if data is None or (isinstance(data, list) and not data):
            return
        # Convert DataFrame to list of dicts if necessary
        if isinstance(data, pd.DataFrame):
            rows = data.to_dict(orient="records")
        else:  # Assume list of BaseModel objects
            rows = [d.dict() for d in data]
        # Group rows by vectorize_by fields
        grouped: Dict[tuple, List[Dict[str, Any]]] = {}
        for row in rows:
            key = tuple(row[f] for f in self.vectorize_by) if self.vectorize_by else ("all",)
            grouped.setdefault(key, []).append(row)
        # Write each group to its own CSV
        for key, group_rows in grouped.items():
            file_path = self._get_file_path(group_rows[0])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=group_rows[0].keys())
                writer.writeheader()
                writer.writerows(group_rows)


    def read(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[T]]:
        """
        Read CSV data, optionally filtered by vectorized field values.

        :param filters: Dict of vectorize_by field names and values to filter by. If None, read all files.
        :return: List of schema objects (T) loaded from CSV files.
        """
        if not self.base_path or not os.path.exists(self.base_path):
            return None

        all_data: List[T] = []

        for root, _, files in os.walk(self.base_path):
            for fname in files:
                if not fname.endswith(".csv"):
                    continue

                # Skip files that do not match filters
                if filters and self.vectorize_by:
                    matches = True
                    for f in self.vectorize_by:
                        value = filters.get(f)
                        if value is not None and f"_{f}_{value}_" not in fname and not fname.endswith(
                                f"_{f}_{value}.csv"):
                            matches = False
                            break
                    if not matches:
                        continue

                # Read CSV
                file_path = os.path.join(root, fname)
                with open(file_path, mode="r", newline="") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    for row in rows:
                        all_data.append(self.schema_class(**row))

        return all_data


    def to_dataframe(self, data: Optional[List[T]] = None) -> pd.DataFrame:
        """
        Convert list of schema objects to pandas DataFrame.

        :param data: List of schema objects (T). If None, will raise ValueError.
        :return: pandas DataFrame.
        """
        if data is None:
            raise ValueError("No data provided to convert to DataFrame.")
        rows = [d.dict() for d in data]
        return pd.DataFrame(rows)
