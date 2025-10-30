import configparser
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
from enum import Enum, auto
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from commons.parametrization.PythonParametrization import PythonParametrization

# -----------------------------
# Enums / Result definitions
# -----------------------------
class HistDataPipelineStage(Enum):
    """Logical pipeline phase identifiers for an historical data pipeline."""
    CONNECT = auto()
    DUMP = auto()
    PROCESS = auto()
    STORE = auto()

class StageResult(Enum):
    SUCCESS = auto()
    SUCCESS_WITH_WARNINGS = auto()
    FAIL = auto()

# -----------------------------
# Pipeline context
# -----------------------------
@dataclass
class PipelineContext:
    """Runtime context for the entire pipeline."""
    params: configparser.ConfigParser
    logger: logging.Logger
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=lambda: {"run_id": datetime.utcnow().isoformat()})

    def add_artifact(self, key: str, value: Any) -> None:
        self.artifacts[key] = value
        self.logger.debug(f"Artifact added: {key} ({type(value).__name__})")


# -----------------------------
# Base stage
# -----------------------------
class BaseStage(ABC):
    """Abstract base class for all stages."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, ctx: PipelineContext) -> Tuple[StageResult, str]:
        ...