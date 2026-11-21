"""Domain models for incident investigations.

Day 8 scope: the first Investigation and Evidence domain models.

The model is deliberately small and framework-free:

* ``Evidence`` is an abstract, immutable value object. Every concrete
  evidence type is a frozen dataclass, so a collected fact cannot be
  edited after it has been recorded.
* ``Investigation`` is a mutable aggregate. It *composes* one existing
  ``Incident`` and owns its evidence collection. State changes go through
  ``start()``, ``add_evidence()`` and ``complete()`` so the lifecycle
  rules live in one place.

These are domain objects, not database rows, API schemas or monitoring
clients. Persistence and transport arrive in later roadmap days.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from math import isfinite

from ..incidents.models import Incident
from ..ingestion.jsonl import LOG_LEVELS, LogRecord


class InvestigationStatus(StrEnum):
    """Lifecycle state of one investigation."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DeploymentStatus(StrEnum):
    """Outcome of a deployment observed as evidence."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    ROLLED_BACK = "rolled_back"


def _require_non_empty(value: object, field_name: str) -> None:
    """Reject a missing, blank or non-string required text field."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_timezone_aware(value: object, field_name: str) -> None:
    """Reject timestamps that do not carry a timezone."""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class Evidence(ABC):
    """One immutable piece of information collected during an investigation.

    ``Evidence`` cannot be instantiated directly: it exists to define the
    common contract that concrete evidence types share. Callers that only
    need to read evidence can depend on this abstraction instead of the
    concrete subclasses.
    """

    evidence_id: str
    source: str
    observed_at: datetime

    def __post_init__(self) -> None:
        _require_non_empty(self.evidence_id, "evidence_id")
        _require_non_empty(self.source, "source")
        _require_timezone_aware(self.observed_at, "observed_at")

    @property
    @abstractmethod
    def summary(self) -> str:
        """Return a short, human-readable description of this evidence."""


@dataclass(frozen=True, slots=True)
class LogEvidence(Evidence):
    """Evidence taken from an application log line."""

    service_name: str
    level: str
    message: str

    def __post_init__(self) -> None:
        # ``slots=True`` recreates the class, which breaks zero-argument
        # ``super()`` in Python 3.12. Call the base validator explicitly.
        Evidence.__post_init__(self)
        _require_non_empty(self.service_name, "service_name")
        _require_non_empty(self.message, "message")
        if (
            not isinstance(self.level, str)
            or self.level.strip().upper() not in LOG_LEVELS
        ):
            raise ValueError("level must be one of " + ", ".join(sorted(LOG_LEVELS)))
        object.__setattr__(self, "level", self.level.strip().upper())

    @classmethod
    def from_log_record(
        cls,
        record: LogRecord,
        *,
        evidence_id: str,
        source: str,
        observed_at: datetime,
    ) -> LogEvidence:
        """Build evidence from a validated Day 6 ``LogRecord``.

        Reusing the ingestion record keeps log parsing in one place instead
        of duplicating the JSONL validation rules here.
        """
        return cls(
            evidence_id=evidence_id,
            source=source,
            observed_at=observed_at,
            service_name=record.service,
            level=record.level,
            message=record.message,
        )

    @property
    def summary(self) -> str:
        return f"[{self.level}] {self.service_name}: {self.message}"


@dataclass(frozen=True, slots=True)
class MetricEvidence(Evidence):
    """A numeric measurement observed for a service over a time window."""

    service_name: str
    metric_name: str
    value: float
    unit: str
    window_seconds: int

    def __post_init__(self) -> None:
        Evidence.__post_init__(self)
        _require_non_empty(self.service_name, "service_name")
        _require_non_empty(self.metric_name, "metric_name")
        _require_non_empty(self.unit, "unit")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError("value must be a number")
        if not isfinite(self.value):
            raise ValueError("value must be finite")
        if isinstance(self.window_seconds, bool) or not isinstance(
            self.window_seconds, int
        ):
            raise TypeError("window_seconds must be an integer")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")
        object.__setattr__(self, "value", float(self.value))

    @property
    def summary(self) -> str:
        return (
            f"{self.service_name} {self.metric_name}={self.value:g}{self.unit} "
            f"over {self.window_seconds}s"
        )


@dataclass(frozen=True, slots=True)
class DeploymentEvidence(Evidence):
    """A deployment that may be related to the incident."""

    service_name: str
    deployment_id: str
    version: str
    environment: str
    status: DeploymentStatus

    def __post_init__(self) -> None:
        Evidence.__post_init__(self)
        _require_non_empty(self.service_name, "service_name")
        _require_non_empty(self.deployment_id, "deployment_id")
        _require_non_empty(self.version, "version")
        _require_non_empty(self.environment, "environment")
        if not isinstance(self.status, DeploymentStatus):
            raise ValueError("status must be a DeploymentStatus value")

    @property
    def summary(self) -> str:
        return (
            f"{self.service_name} deployment {self.deployment_id} "
            f"({self.version}) to {self.environment}: {self.status.value}"
        )


@dataclass(slots=True)
class Investigation:
    """Mutable aggregate that owns one incident and its collected evidence.

    An investigation *has* an incident; it is not an incident. Composition
    keeps the incident immutable while allowing the investigation to evolve
    through its lifecycle.
    """

    investigation_id: str
    incident: Incident
    created_at: datetime
    _status: InvestigationStatus = field(
        default=InvestigationStatus.OPEN,
        init=False,
        repr=False,
    )
    _evidence: list[Evidence] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        _require_non_empty(self.investigation_id, "investigation_id")
        if not isinstance(self.incident, Incident):
            raise TypeError("incident must be an Incident")
        _require_timezone_aware(self.created_at, "created_at")

    @property
    def status(self) -> InvestigationStatus:
        """Read-only lifecycle status."""
        return self._status

    @property
    def evidence(self) -> tuple[Evidence, ...]:
        """Read-only snapshot of the collected evidence."""
        return tuple(self._evidence)

    def start(self) -> None:
        """Move an OPEN investigation into IN_PROGRESS."""
        if self._status is not InvestigationStatus.OPEN:
            raise ValueError(
                f"cannot start an investigation in status '{self._status.value}'"
            )
        self._status = InvestigationStatus.IN_PROGRESS

    def complete(self) -> None:
        """Move an IN_PROGRESS investigation into COMPLETED."""
        if self._status is not InvestigationStatus.IN_PROGRESS:
            raise ValueError(
                f"cannot complete an investigation in status '{self._status.value}'"
            )
        self._status = InvestigationStatus.COMPLETED

    def add_evidence(self, evidence: Evidence) -> None:
        """Attach evidence to an IN_PROGRESS investigation.

        The aggregate depends on the ``Evidence`` abstraction, so new
        evidence types can be added without changing this method.
        """
        if not isinstance(evidence, Evidence):
            raise TypeError("evidence must be an Evidence instance")
        if self._status is not InvestigationStatus.IN_PROGRESS:
            raise ValueError(
                "evidence can only be added while the investigation is in progress"
            )
        if any(
            collected.evidence_id == evidence.evidence_id
            for collected in self._evidence
        ):
            raise ValueError(f"duplicate evidence_id: {evidence.evidence_id}")
        self._evidence.append(evidence)
