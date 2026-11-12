from opspilot.incidents import (
    Incident,
    IncidentPriority,
    PrioritizationResult,
    create_incident,
    generate_incident_id,
    prioritize_incident,
)
from opspilot.incidents.models import Incident as ModelIncident
from opspilot.incidents.prioritization import Incident as LegacyIncident


def test_package_exports_domain_api() -> None:
    incident = create_incident(
        service_name="search",
        severity="medium",
        is_production=False,
        affected_users=5,
    )
    result = prioritize_incident(incident)

    assert isinstance(incident, Incident)
    assert isinstance(incident, ModelIncident)
    assert isinstance(incident, LegacyIncident)
    assert isinstance(result, PrioritizationResult)
    assert result.priority is IncidentPriority.P3
    assert len(generate_incident_id()) == 36


def test_prioritization_result_keeps_incident_id() -> None:
    incident = Incident(
        incident_id="inc-existing",
        service_name="catalog",
        severity="high",
        is_production=False,
        affected_users=1,
    )

    assert prioritize_incident(incident).incident_id == "inc-existing"
