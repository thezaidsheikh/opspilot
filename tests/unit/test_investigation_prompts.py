"""Tests for incident investigation prompt templates (Day 6)."""

from opspilot.incidents import create_incident
from opspilot.investigation import SYSTEM_PROMPT, incident_summary_prompt


def test_system_prompt_states_grounding_rule() -> None:
    assert "Answer only from the evidence provided" in SYSTEM_PROMPT
    assert "I don't know" in SYSTEM_PROMPT


def test_summary_prompt_includes_incident_facts() -> None:
    incident = create_incident(
        service_name="payment-api",
        severity="critical",
        is_production=True,
        affected_users=1200,
    )

    prompt = incident_summary_prompt(
        incident, evidence="ERROR payment timeout after 5000ms"
    )

    assert incident.incident_id in prompt
    assert "payment-api" in prompt
    assert "critical" in prompt
    assert "1200" in prompt
    assert "ERROR payment timeout after 5000ms" in prompt


def test_summary_prompt_without_evidence_says_so_explicitly() -> None:
    incident = create_incident(
        service_name="checkout",
        severity="high",
        is_production=False,
        affected_users=0,
    )

    prompt = incident_summary_prompt(incident)

    assert "No evidence retrieved yet." in prompt
    assert "I don't know" in prompt
