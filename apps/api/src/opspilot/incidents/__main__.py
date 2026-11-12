"""Run a small incident prioritization example with ``python -m``."""

from . import create_incident, prioritize_incident


def main() -> None:
    incident = create_incident(
        service_name="payments-api",
        severity="critical",
        is_production=True,
        affected_users=250,
    )
    result = prioritize_incident(incident)
    print(f"Incident: {incident.incident_id}")
    print(f"Service: {incident.service_name}")
    print(f"Priority: {result.priority}")
    print(f"Reasons: {', '.join(result.reasons)}")


if __name__ == "__main__":
    main()
