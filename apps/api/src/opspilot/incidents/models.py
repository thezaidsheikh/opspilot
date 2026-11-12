"""Domain models for incident investigation."""

from dataclasses import dataclass
from enum import StrEnum


class IncidentPriority(StrEnum):
    """Operational response priority."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass(frozen=True)
class Incident:
    """Validated facts used to prioritize an incident."""

    incident_id: str
    service_name: str
    severity: str
    is_production: bool
    affected_users: int

    def __post_init__(self) -> None:
        if not self.incident_id.strip():
            raise ValueError("incident_id must not be empty")
        if not self.service_name.strip():
            raise ValueError("service_name must not be empty")
        if self.severity not in {"critical", "high", "medium", "low"}:
            raise ValueError("severity must be critical, high, medium, or low")
        if self.affected_users < 0:
            raise ValueError("affected_users must not be negative")


@dataclass(frozen=True)
class PrioritizationResult:
    """Priority and human-readable reasons for the decision."""

    incident_id: str
    priority: IncidentPriority
    reasons: tuple[str, ...]
