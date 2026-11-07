import pytest

from opspilot.incidents import (
    Incident,
    IncidentPriority,
    prioritize_incident,
)


def test_critical_production_incident_is_p1() -> None:
    incident = Incident(
        incident_id="inc-001",
        service_name="payments",
        severity="critical",
        is_production=True,
        affected_users=25,
    )

    result = prioritize_incident(incident)

    assert result.priority is IncidentPriority.P1
    assert result.reasons == ("critical severity", "production service")


def test_large_user_impact_is_p1() -> None:
    incident = Incident(
        incident_id="inc-002",
        service_name="search",
        severity="medium",
        is_production=False,
        affected_users=1_000,
    )

    result = prioritize_incident(incident)

    assert result.priority is IncidentPriority.P1
    assert "at least 1000 users are affected" in result.reasons


def test_high_severity_is_p2() -> None:
    incident = Incident(
        incident_id="inc-003",
        service_name="catalog",
        severity="high",
        is_production=False,
        affected_users=10,
    )

    result = prioritize_incident(incident)

    assert result.priority is IncidentPriority.P2
    assert result.reasons == ("no elevated severity or production impact was reported",)


def test_low_severity_nonproduction_is_p3() -> None:
    incident = Incident(
        incident_id="inc-004",
        service_name="staging-worker",
        severity="low",
        is_production=False,
        affected_users=0,
    )

    result = prioritize_incident(incident)

    assert result.priority is IncidentPriority.P3
    assert result.reasons == ("no elevated severity or production impact was reported",)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("incident_id", " ", "incident_id must not be empty"),
        ("service_name", "", "service_name must not be empty"),
        ("severity", "urgent", "severity must be critical, high, medium, or low"),
        ("affected_users", -1, "affected_users must not be negative"),
    ],
)
def test_invalid_incident_data_raises_value_error(
    field: str,
    value: object,
    message: str,
) -> None:
    values: dict[str, object] = {
        "incident_id": "inc-005",
        "service_name": "api",
        "severity": "low",
        "is_production": False,
        "affected_users": 0,
    }
    values[field] = value

    with pytest.raises(ValueError, match=message):
        Incident(**values)  # type: ignore[arg-type]


def test_keyword_only_threshold_can_be_overridden() -> None:
    incident = Incident(
        incident_id="inc-006",
        service_name="api",
        severity="low",
        is_production=False,
        affected_users=50,
    )

    result = prioritize_incident(incident, p1_user_threshold=50)

    assert result.priority is IncidentPriority.P1


def test_threshold_must_be_positive() -> None:
    incident = Incident(
        incident_id="inc-007",
        service_name="api",
        severity="low",
        is_production=False,
        affected_users=0,
    )

    with pytest.raises(ValueError, match="p1_user_threshold must be at least 1"):
        prioritize_incident(incident, p1_user_threshold=0)
