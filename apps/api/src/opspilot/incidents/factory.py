"""Factories for constructing incident domain objects."""

from .identifiers import generate_incident_id
from .models import Incident


def create_incident(
    *,
    service_name: str,
    severity: str,
    is_production: bool,
    affected_users: int,
) -> Incident:
    """Create an incident with a generated ID and validated domain data."""
    return Incident(
        incident_id=generate_incident_id(),
        service_name=service_name,
        severity=severity,
        is_production=is_production,
        affected_users=affected_users,
    )
