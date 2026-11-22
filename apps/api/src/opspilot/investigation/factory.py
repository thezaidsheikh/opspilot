"""Factories for constructing investigation domain objects."""

from datetime import UTC, datetime
from uuid import uuid4

from ..incidents.models import Incident
from .models import Investigation


def create_investigation(*, incident: Incident) -> Investigation:
    """Create a new OPEN investigation for an existing incident.

    The incident is reused, not copied or mutated. The investigation gets
    its own UUID4 identifier so the two domain concepts stay separate.
    """
    return Investigation(
        investigation_id=str(uuid4()),
        incident=incident,
        created_at=datetime.now(UTC),
    )
