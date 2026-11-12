"""Deterministic incident prioritization business logic."""

from .models import Incident, IncidentPriority, PrioritizationResult


def prioritize_incident(
    incident: Incident,
    *,
    p1_user_threshold: int = 1_000,
) -> PrioritizationResult:
    """Assign an incident priority from its known impact.

    `p1_user_threshold` is keyword-only so callers must name the policy
    setting explicitly when overriding its default.
    """
    if p1_user_threshold < 1:
        raise ValueError("p1_user_threshold must be at least 1")

    reasons: list[str] = []

    if incident.severity == "critical":
        reasons.append("critical severity")
    if incident.is_production:
        reasons.append("production service")
    if incident.affected_users >= p1_user_threshold:
        reasons.append(f"at least {p1_user_threshold} users are affected")

    if incident.severity == "critical" and incident.is_production:
        priority = IncidentPriority.P1
    elif incident.affected_users >= p1_user_threshold:
        priority = IncidentPriority.P1
    elif incident.severity == "high" or incident.is_production:
        priority = IncidentPriority.P2
    else:
        priority = IncidentPriority.P3

    if not reasons:
        reasons.append("no elevated severity or production impact was reported")

    return PrioritizationResult(
        incident_id=incident.incident_id,
        priority=priority,
        reasons=tuple(reasons),
    )
