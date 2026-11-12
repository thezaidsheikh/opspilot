"""Incident identifier generation."""

from uuid import uuid4


def generate_incident_id() -> str:
    """Return a unique UUID4 string for a newly created incident."""
    return str(uuid4())
