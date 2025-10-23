"""
Generic, fully decoupled data pipeline skeleton.

Goals:
- No reference to specific data schemas or storage types.
- Generic orchestration of any Dump → Process → Store pipeline.
- Each stage is a pluggable strategy implementing IStage[T].
- Supports multiple stages per logical phase.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Dict, Any, List, Tuple, Protocol, Callable
from enum import Enum, auto
import logging
from abc import ABC, abstractmethod
from datetime import datetime

from storage.ISchemaStorage import ISchemaStorage

# -----------------------------
# Generic type for data payload
# -----------------------------
T = TypeVar('T')  # Could be DataFrame, list of records, domain object, etc.


# -----------------------------
# Enums / Result definitions
# -----------------------------
class DataPipelinePhase(Enum):
    """Logical pipeline phase identifiers."""
    CONNECT = auto()
    DUMP = auto()
    PROCESS = auto()
    STORE = auto()


class StageResult(Enum):
    SUCCESS = auto()
    SUCCESS_WITH_WARNINGS = auto()
    FAIL = auto()


# -----------------------------
# Generic stage
# -----------------------------
class IStage(Protocol, Generic[T]):
    """Each stage receives a PipelineContext and returns a (success, message) tuple."""
    def run(self, ctx: PipelineContext[T]) -> Tuple[bool, str]: ...


# -----------------------------
# Pipeline context
# -----------------------------
@dataclass
class PipelineContext(Generic[T]):
    """Runtime context for the entire pipeline."""
    params: Dict[str, Any]
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("Pipeline"))
    storage: Optional[ISchemaStorage[T]] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=lambda: {"run_id": datetime.utcnow().isoformat()})

    def add_artifact(self, key: str, value: Any) -> None:
        self.artifacts[key] = value
        self.logger.debug(f"Artifact added: {key} ({type(value).__name__})")


# -----------------------------
# Base stage
# -----------------------------
class BaseStage(Generic[T], ABC):
    """Abstract base class for all stages."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, ctx: PipelineContext[T]) -> Tuple[bool, str]:
        ...


# -----------------------------
# Pipeline runner
# -----------------------------
@dataclass
class GenericPipeline(Generic[T]):
    """
    Generic pipeline orchestrator.

    - Each phase can have multiple stages (executed sequentially).
    - Each stage is pluggable and type-agnostic.
    - No data model or storage specifics.
    """
    stages: Dict[DataPipelinePhase, List[IStage[T]]]
    ctx: PipelineContext[T]

    def run(self, stop_on_fail: bool = True) -> Dict[str, List[Tuple[str, StageResult, str]]]:
        results: Dict[str, List[Tuple[str, StageResult, str]]] = {}
        self.ctx.logger.info(f"Pipeline started (run_id={self.ctx.metadata['run_id']})")

        for phase in DataPipelinePhase:
            phase_name = phase.name
            results[phase_name] = []

            stage_list = self.stages.get(phase, [])
            if not stage_list:
                results[phase_name].append(("__none__", StageResult.SUCCESS_WITH_WARNINGS, "No stages"))
                continue

            for stage in stage_list:
                stage_name = stage.__class__.__name__
                self.ctx.logger.info(f"[{phase_name}] Running stage {stage_name}")
                ok, msg = stage.run(self.ctx)
                result_enum = StageResult.SUCCESS if ok else StageResult.FAIL
                results[phase_name].append((stage_name, result_enum, msg))
                self.ctx.logger.info(f"[{phase_name}] {stage_name} → {result_enum.name}: {msg}")

                if stop_on_fail and not ok:
                    self.ctx.logger.error(f"Stopping pipeline due to failure in {stage_name}")
                    return results

        self.ctx.logger.info("Pipeline completed successfully.")
        return results
