"""Incident investigation package (prompts, tools, workflow)."""

from .prompts import SYSTEM_PROMPT, incident_summary_prompt

__all__ = [
    "SYSTEM_PROMPT",
    "incident_summary_prompt",
]
