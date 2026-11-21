"""Tests for the Day 8 investigation and evidence domain models."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from opspilot.incidents import Incident, create_incident
from opspilot.ingestion import LogRecord
from opspilot.investigation import (
    DeploymentEvidence,
    DeploymentStatus,
    Evidence,
    Investigation,
    InvestigationStatus,
    LogEvidence,
    MetricEvidence,
    create_investigation,
)

OBSERVED_AT = datetime(2026, 11, 21, 10, 30, tzinfo=UTC)

EvidenceFactory = Callable[..., Evidence]


def make_log_evidence(
    *,
    evidence_id: str = "ev-log-1",
    source: str = "incident-log.jsonl",
    observed_at: datetime = OBSERVED_AT,
) -> LogEvidence:
    return LogEvidence(
        evidence_id=evidence_id,
        source=source,
        observed_at=observed_at,
        service_name="payments",
        level="ERROR",
        message="payment timeout after 5000ms",
    )


def make_metric_evidence(
    *,
    evidence_id: str = "ev-metric-1",
    source: str = "prometheus",
    observed_at: datetime = OBSERVED_AT,
    metric_name: str = "http_request_duration_p95",
    value: float = 250.5,
    unit: str = "ms",
    window_seconds: int = 60,
) -> MetricEvidence:
    return MetricEvidence(
        evidence_id=evidence_id,
        source=source,
        observed_at=observed_at,
        service_name="payments",
        metric_name=metric_name,
        value=value,
        unit=unit,
        window_seconds=window_seconds,
    )


def make_deployment_evidence(
    *,
    evidence_id: str = "ev-deploy-1",
    source: str = "deployment-history",
    observed_at: datetime = OBSERVED_AT,
    status: DeploymentStatus = DeploymentStatus.SUCCEEDED,
) -> DeploymentEvidence:
    return DeploymentEvidence(
        evidence_id=evidence_id,
        source=source,
        observed_at=observed_at,
        service_name="payments",
        deployment_id="deploy-4242",
        version="2.8.1",
        environment="production",
        status=status,
    )


EVIDENCE_FACTORIES: tuple[EvidenceFactory, ...] = (
    make_log_evidence,
    make_metric_evidence,
    make_deployment_evidence,
)


def make_incident() -> Incident:
    return create_incident(
        service_name="payments",
        severity="critical",
        is_production=True,
        affected_users=1_200,
    )


def make_investigation() -> Investigation:
    return create_investigation(incident=make_incident())


def started_investigation() -> Investigation:
    investigation = make_investigation()
    investigation.start()
    return investigation


# --- Evidence abstraction and inheritance ---------------------------------


def test_evidence_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError, match="abstract"):
        Evidence(  # type: ignore[abstract]
            evidence_id="ev-1",
            source="logs",
            observed_at=OBSERVED_AT,
        )


@pytest.mark.parametrize("factory", EVIDENCE_FACTORIES)
def test_concrete_evidence_is_an_evidence(factory: EvidenceFactory) -> None:
    assert isinstance(factory(), Evidence)


def test_each_evidence_type_implements_the_common_summary() -> None:
    log = make_log_evidence()
    metric = make_metric_evidence()
    deployment = make_deployment_evidence()

    assert "ERROR" in log.summary
    assert "payments" in log.summary
    assert "payment timeout after 5000ms" in log.summary

    assert "http_request_duration_p95" in metric.summary
    assert "250.5ms" in metric.summary
    assert "over 60s" in metric.summary

    assert "deploy-4242" in deployment.summary
    assert "2.8.1" in deployment.summary
    assert "production" in deployment.summary
    assert "succeeded" in deployment.summary


@pytest.mark.parametrize("factory", EVIDENCE_FACTORIES)
@pytest.mark.parametrize("field_name", ["evidence_id", "source"])
def test_evidence_rejects_blank_common_fields(
    factory: EvidenceFactory, field_name: str
) -> None:
    with pytest.raises(ValueError, match=f"{field_name} must be a non-empty string"):
        factory(**{field_name: "   "})


@pytest.mark.parametrize("factory", EVIDENCE_FACTORIES)
def test_evidence_rejects_naive_timestamps(factory: EvidenceFactory) -> None:
    with pytest.raises(ValueError, match="observed_at must be timezone-aware"):
        factory(observed_at=datetime(2026, 11, 21, 10, 30))


@pytest.mark.parametrize("factory", EVIDENCE_FACTORIES)
def test_evidence_is_frozen(factory: EvidenceFactory) -> None:
    evidence = factory()

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_id = "ev-changed"  # type: ignore


# --- LogEvidence -----------------------------------------------------------


def test_log_evidence_normalises_level_to_upper_case() -> None:
    evidence = LogEvidence(
        evidence_id="ev-log-2",
        source="incident-log.jsonl",
        observed_at=OBSERVED_AT,
        service_name="search",
        level="warning",
        message="slow query",
    )

    assert evidence.level == "WARNING"
    assert evidence.summary.startswith("[WARNING] search:")


def test_log_evidence_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="level must be one of"):
        LogEvidence(
            evidence_id="ev-log-3",
            source="incident-log.jsonl",
            observed_at=OBSERVED_AT,
            service_name="search",
            level="FATAL",
            message="slow query",
        )


def test_log_evidence_reuses_day_six_log_record() -> None:
    record = LogRecord(
        level="WARNING",
        service="search",
        message="slow query",
        line_number=7,
    )

    evidence = LogEvidence.from_log_record(
        record,
        evidence_id="ev-log-7",
        source="incident-log.jsonl",
        observed_at=OBSERVED_AT,
    )

    assert evidence.service_name == "search"
    assert evidence.level == "WARNING"
    assert evidence.message == "slow query"
    assert evidence.summary == "[WARNING] search: slow query"


# --- MetricEvidence --------------------------------------------------------


@pytest.mark.parametrize("value", [250.5, 0.0, -3.5])
def test_metric_evidence_accepts_finite_values(value: float) -> None:
    assert make_metric_evidence(value=value).value == value


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_metric_evidence_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError, match="value must be finite"):
        make_metric_evidence(value=value)


def test_metric_evidence_rejects_blank_metric_name() -> None:
    with pytest.raises(ValueError, match="metric_name must be a non-empty string"):
        make_metric_evidence(metric_name=" ")


def test_metric_evidence_rejects_blank_unit() -> None:
    with pytest.raises(ValueError, match="unit must be a non-empty string"):
        make_metric_evidence(unit=" ")


@pytest.mark.parametrize("window_seconds", [0, -1])
def test_metric_evidence_rejects_non_positive_window(window_seconds: int) -> None:
    with pytest.raises(ValueError, match="window_seconds must be greater than zero"):
        make_metric_evidence(window_seconds=window_seconds)


# --- DeploymentEvidence ----------------------------------------------------


def test_deployment_evidence_requires_the_status_enum() -> None:
    with pytest.raises(ValueError, match="status must be a DeploymentStatus value"):
        make_deployment_evidence(status="failed")  # type: ignore[arg-type]


# --- Investigation composition --------------------------------------------


def test_investigation_composes_the_incident() -> None:
    incident = make_incident()
    investigation = create_investigation(incident=incident)

    assert investigation.incident is incident
    assert investigation.investigation_id != incident.incident_id


def test_investigation_starts_open_without_evidence() -> None:
    investigation = make_investigation()

    assert investigation.status is InvestigationStatus.OPEN
    assert investigation.evidence == ()
    assert isinstance(investigation.evidence, tuple)


def test_investigations_have_independent_evidence_collections() -> None:
    first = started_investigation()
    second = started_investigation()

    first.add_evidence(make_log_evidence())

    assert len(first.evidence) == 1
    assert second.evidence == ()


def test_multiple_evidence_subclasses_can_be_added() -> None:
    investigation = started_investigation()

    investigation.add_evidence(make_log_evidence())
    investigation.add_evidence(make_metric_evidence())
    investigation.add_evidence(make_deployment_evidence())

    assert [type(item) for item in investigation.evidence] == [
        LogEvidence,
        MetricEvidence,
        DeploymentEvidence,
    ]
    assert all(isinstance(item, Evidence) for item in investigation.evidence)
    assert all(item.summary for item in investigation.evidence)


def test_duplicate_evidence_ids_are_rejected() -> None:
    investigation = started_investigation()
    investigation.add_evidence(make_log_evidence(evidence_id="ev-shared"))

    with pytest.raises(ValueError, match="duplicate evidence_id: ev-shared"):
        investigation.add_evidence(make_metric_evidence(evidence_id="ev-shared"))

    assert len(investigation.evidence) == 1


def test_evidence_view_is_a_read_only_snapshot() -> None:
    investigation = started_investigation()
    first = make_log_evidence(evidence_id="ev-1")
    investigation.add_evidence(first)

    snapshot = investigation.evidence
    investigation.add_evidence(make_metric_evidence(evidence_id="ev-2"))

    assert snapshot == (first,)
    assert len(investigation.evidence) == 2
    with pytest.raises(AttributeError):
        snapshot.append(first)  # type: ignore[attr-defined]


# --- Investigation lifecycle ----------------------------------------------


def test_start_moves_open_to_in_progress() -> None:
    investigation = make_investigation()

    investigation.start()

    assert investigation.status is InvestigationStatus.IN_PROGRESS


def test_complete_moves_in_progress_to_completed() -> None:
    investigation = started_investigation()

    investigation.complete()

    assert investigation.status is InvestigationStatus.COMPLETED


def test_start_rejects_an_already_started_investigation() -> None:
    investigation = started_investigation()

    with pytest.raises(ValueError, match="cannot start"):
        investigation.start()

    assert investigation.status is InvestigationStatus.IN_PROGRESS


def test_complete_rejects_an_open_investigation() -> None:
    investigation = make_investigation()

    with pytest.raises(ValueError, match="cannot complete"):
        investigation.complete()

    assert investigation.status is InvestigationStatus.OPEN


def test_adding_evidence_before_start_is_rejected() -> None:
    investigation = make_investigation()

    with pytest.raises(ValueError, match="in progress"):
        investigation.add_evidence(make_log_evidence())

    assert investigation.evidence == ()


def test_adding_evidence_after_completion_is_rejected() -> None:
    investigation = started_investigation()
    investigation.add_evidence(make_log_evidence())
    investigation.complete()

    with pytest.raises(ValueError, match="in progress"):
        investigation.add_evidence(make_metric_evidence())

    assert len(investigation.evidence) == 1
    assert investigation.status is InvestigationStatus.COMPLETED


def test_status_cannot_be_assigned_directly() -> None:
    investigation = make_investigation()

    with pytest.raises(AttributeError):
        investigation.status = InvestigationStatus.COMPLETED  # type: ignore

    assert investigation.status is InvestigationStatus.OPEN


def test_investigation_rejects_a_naive_created_at() -> None:
    with pytest.raises(ValueError, match="created_at must be timezone-aware"):
        Investigation(
            investigation_id="inv-1",
            incident=make_incident(),
            created_at=datetime(2026, 11, 21, 10, 30),
        )


# --- Factory ---------------------------------------------------------------


def test_factory_creates_a_valid_investigation() -> None:
    incident = make_incident()
    investigation = create_investigation(incident=incident)

    assert isinstance(investigation, Investigation)
    assert investigation.incident is incident
    assert investigation.status is InvestigationStatus.OPEN
    assert investigation.evidence == ()
    assert investigation.created_at.tzinfo is not None
    assert investigation.created_at.utcoffset() is not None


def test_factory_generates_a_uuid4_investigation_id() -> None:
    investigation = make_investigation()

    assert UUID(investigation.investigation_id).version == 4


def test_factory_investigation_id_differs_from_the_incident_id() -> None:
    incident = make_incident()
    investigation = create_investigation(incident=incident)

    assert investigation.investigation_id != incident.incident_id


def test_factory_generates_unique_ids_for_separate_calls() -> None:
    first = make_investigation()
    second = make_investigation()

    assert first.investigation_id != second.investigation_id


def test_factory_requires_keyword_arguments() -> None:
    incident = make_incident()

    with pytest.raises(TypeError):
        create_investigation(incident)  # type: ignore[misc]
