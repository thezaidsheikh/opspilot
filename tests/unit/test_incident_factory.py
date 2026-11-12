from uuid import UUID

import pytest

from opspilot.incidents import create_incident


def test_factory_creates_incident_with_uuid4_identifier() -> None:
    incident = create_incident(
        service_name="payments",
        severity="critical",
        is_production=True,
        affected_users=42,
    )

    parsed_id = UUID(incident.incident_id)
    assert parsed_id.version == 4
    assert incident.service_name == "payments"
    assert incident.severity == "critical"
    assert incident.is_production is True
    assert incident.affected_users == 42


def test_factory_rejects_invalid_domain_data() -> None:
    with pytest.raises(ValueError, match="service_name must not be empty"):
        create_incident(
            service_name=" ",
            severity="low",
            is_production=False,
            affected_users=0,
        )


def test_factory_requires_keyword_arguments() -> None:
    with pytest.raises(TypeError):
        create_incident("payments", "critical", True, 42)  # type: ignore[misc]
