import pandas as pd
import configparser

from typing import TypeVar, Generic, Optional, List, Type, Dict, Any, Union
from pydantic import BaseModel
from sqlalchemy import Table, MetaData, insert, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from storage.sqldb.SqlGenerics import *

T = TypeVar("T", bound=BaseModel)

class SQLSchemaStorage(Generic[T]):
    """
    Generic SQL storage for schema objects or DataFrames.

    Design:
    --------
    - Schema-driven storage: each row represents a Pydantic schema object T.
    - Vectorize-by sharding on write is NOT supported; all data goes into a single existing table.
    - Filtering is supported on read:
        - By vectorize fields (filters dict)
        - Or via a SQL WHERE clause string (custom_filter)
    - Database engine and connection are configured from an INI config file.
    """

    def __init__(self,
                 schema_class: Type[T],
                 vectorize_by: Optional[List[str]] = None,
                 config_section: str = "DbStorage",
                 key_db_type: str = "DbType",
                 key_host: str = "DbHost",
                 key_port: str = "DbPort",
                 key_user: str = "DbUser",
                 key_pswd: str = "DbPassword",
                 key_name: str = "DbName",
                 key_table_name: str = "DbTable"):
        """
        Initialize the SQL schema storage.

        :param schema_class: Pydantic model class representing schema T
        :param vectorize_by: Fields that can be used for filtering (read only)
        :param config_section: INI section for database config
        :param key_*: Keys in the INI file for database connection parameters
        :param key_table_name: Key in the INI file for the table name
        """
        self.schema_class = schema_class
        self.vectorize_by = vectorize_by or []
        self.config_section = config_section
        self.key_db_type = key_db_type
        self.key_host = key_host
        self.key_port = key_port
        self.key_user = key_user
        self.key_pswd = key_pswd
        self.key_name = key_name
        self.key_table_name = key_table_name

        self.engine: Optional[Engine] = None
        self.metadata = MetaData()
        self.table: Optional[Table] = None
        self.Session = None


    def configure_from_config(self, config_path: str) -> None:
        """
        Read database connection parameters and table name from a config.ini file
        and create the SQLAlchemy engine.
        """
        parser = configparser.ConfigParser()
        parser.read(config_path)

        section = self.config_section
        if section not in parser:
            raise ValueError(f"Section '{section}' not found in config file {config_path}")

        db_type = DbType[parser[section][self.key_db_type]]
        host = parser[section][self.key_host]
        port = parser[section][self.key_port]
        user = parser[section][self.key_user]
        password = parser[section][self.key_pswd]
        db_name = parser[section][self.key_name]
        table_name = parser[section][self.key_table_name]

        self.engine = sql_alchemy_engine(host, port, db_name, user, password, db_type)
        self.Session = sessionmaker(bind=self.engine)

        # Assume table exists; reflect it
        self.metadata.reflect(bind=self.engine, only=[table_name])
        if table_name not in self.metadata.tables:
            raise ValueError(f"Table '{table_name}' does not exist in the database")
        self.table = self.metadata.tables[table_name]


    def write(self, data: Union[List[T], pd.DataFrame], **kwargs) -> None:
        """
        Write schema objects or DataFrame rows to the SQL table.
        Vectorized sharding on write is NOT supported.
        """
        if self.engine is None or self.table is None:
            raise ValueError("Engine/table not configured. Call configure_from_config first.")

        if data is None or (isinstance(data, list) and not data):
            return

        if isinstance(data, pd.DataFrame):
            rows = data.to_dict(orient="records")
        else:
            rows = [d.dict() for d in data]

        with self.engine.begin() as conn:
            conn.execute(insert(self.table), rows)


    def read(self, filters: Optional[Dict[str, Any]] = None, custom_filter: Optional[str] = None) -> List[T]:
        """
        Read rows from the SQL table.

        :param filters: dict of vectorize fields and values for filtering
        :param custom_filter: optional SQL WHERE clause string, e.g. "a='A1' AND d='D1'"
        :return: list of schema objects
        """
        if self.engine is None or self.table is None:
            raise ValueError("Engine/table not configured. Call configure_from_config first.")

        stmt = select(self.table)
        if filters:
            for k, v in filters.items():
                if k not in self.table.c:
                    continue
                stmt = stmt.where(self.table.c[k] == v)
        if custom_filter:
            stmt = stmt.where(text(custom_filter))

        result = []
        with self.engine.begin() as conn:
            rows = conn.execute(stmt).mappings().all()
            for row in rows:
                result.append(self.schema_class(**row))
        return result


    def to_dataframe(self, data: Optional[List[T]] = None) -> pd.DataFrame:
        """
        Convert list of schema objects to pandas DataFrame.
        """
        if data is None:
            raise ValueError("No data provided to convert to DataFrame.")
        rows = [d.dict() for d in data]
        return pd.DataFrame(rows)
