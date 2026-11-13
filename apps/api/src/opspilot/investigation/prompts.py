"""Prompt templates for incident investigation.

Prompts live in code as named constants and builder functions — never
as hardcoded strings inside a handler. That way they are versioned,
reviewed and tested like any other code, and the grounding rule ("answer
only from the evidence") is enforced in one place instead of being
re-typed — and forgotten — at every call site.

Day 6 scope: one system prompt plus one incident-summary prompt.
Hypothesis generation and RAG prompts arrive with their roadmap days.
"""

from ..incidents.models import Incident

SYSTEM_PROMPT = (
    "You are OpsPilot, an incident investigation assistant. "
    "Answer only from the evidence provided in the prompt. "
    "If the evidence does not contain the answer, say 'I don't know' "
    "instead of guessing. Never invent log lines, config values, or "
    "service names that are not in the evidence."
)


def incident_summary_prompt(incident: Incident, *, evidence: str = "") -> str:
    """Build the user prompt that asks for a short incident summary.

    ``evidence`` is the retrieved context (log lines, runbook excerpts).
    When no evidence was retrieved yet, the prompt says so explicitly —
    the model must then say "I don't know" rather than guess a cause.
    """
    evidence_block = evidence.strip() or "No evidence retrieved yet."
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Incident {incident.incident_id}: {incident.service_name} "
        f"reported severity '{incident.severity}' "
        f"(production: {'yes' if incident.is_production else 'no'}, "
        f"affected users: {incident.affected_users}).\n\n"
        f"Evidence:\n{evidence_block}\n\n"
        "Summarise this incident in 3 bullet points: what happened, "
        "the likely cause, and the next investigation step. "
        "Cite the evidence line each point comes from."
    )
