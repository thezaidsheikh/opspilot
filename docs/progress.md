# Applied AI Engineering Progress

**Curriculum authority:** the 72-day / 12-week Applied AI Engineering roadmap in the AI Engineering project. This tracker records evidence; it does not redefine the roadmap.
**Last reconciled:** 21 Nov 2026
**Current roadmap position:** Day 8 lesson and implementation are complete locally and locally verified; the Day 8 assessment is pending. Day 2 practical evidence, hosted Day 6 CI, and Day 7 assessment details remain open catch-up evidence.

## Evidence-based status

| Day | Roadmap topic | Status | Evidence / remaining work |
|---|---|---|---|
| 1 | Python setup, interpreter, virtual environments, pip, project structure | Studied; repo foundation exists | Learning notes record study. Repository has Python packaging, tests, and CI. |
| 2 | Variables, types, operators, strings, formatting | Studied; practical evidence incomplete | Learning notes record the incident-normalisation exercise; exact committed implementation was not confirmed. Keep this as an evidence gap. |
| 3 | Collections and comprehensions | Studied; implementation evidence exists | Catalog processor and tests are present in repository history. |
| 4 | Conditions, loops, functions, scope, arguments | Studied; implementation evidence exists | Incident prioritisation package and tests are present in repository history. |
| 5 | Modules, packages, imports, standard library | Studied; implementation evidence exists | opspilot.incidents package is committed. |
| 6 | Exceptions, logging, debugging, file handling, JSON | Lesson studied; implementation merged; regression test and local checks complete; hosted CI unconfirmed | PR #2 merged on 16 Nov 2026 as 6d47a8e. Added the missing-service regression test. Local verification on this branch: pytest 66 passed; Ruff lint passed; Ruff format check passed (34 files); Pyright 0 errors. GitHub's commit workflow query returned no runs and combined status returned no checks, so post-merge hosted CI is not confirmed. |
| 7 | Revision, coding assessment, Python interview mock | Complete (user-confirmed) | User confirmed completion on 17 Nov 2026. Assessment score and mock details were not provided and are not inferred. |
| 8 | OOP, classes, inheritance, composition, dataclasses | Lesson delivered; implementation complete locally; local checks passed; assessment pending | Branch `learning/day-08-oop-domain-models`. Added the `Evidence` abstraction, `LogEvidence`, `MetricEvidence`, `DeploymentEvidence`, `Investigation`, `InvestigationStatus` and `create_investigation`. New `tests/unit/test_investigation_models.py` adds 50 tests. Full suite: 116 passed. Ruff lint passed; Ruff format check passed (38 files); Pyright 0 errors. The user assessment has not been attempted, so Day 8 is not marked complete. |

## Day 6 catch-up checklist

- [x] Missing-service JSONL line is skipped, counted, and does not prevent valid neighboring lines from processing.
- [x] Run pytest (66 passed), Ruff lint, Ruff format check (34 files), and Pyright (0 errors) as configured by GitHub Actions.
- [x] Check GitHub Actions for the merge commit; no workflow runs or status checks were returned, so hosted CI remains unconfirmed. A local pass does not establish hosted CI completion.

## Day 7 completion record

- [x] Day 7 marked complete based on the user's confirmation.
- [ ] Assessment score/results details recorded; not supplied, so the 80% phase target cannot be independently checked.
- [ ] Interview mock details recorded; not supplied.

Day 8 implementation evidence is recorded below. Keep the Day 2 practical and Day 6 hosted-CI evidence gaps visible as catch-up; do not describe them as verified.

## Day 8 implementation record

**Branch:** `learning/day-08-oop-domain-models`
**Lesson:** Delivered with this implementation task — OOP, classes, inheritance, composition and dataclasses.
**Implementation:** `apps/api/src/opspilot/investigation/models.py` and `apps/api/src/opspilot/investigation/factory.py`; `apps/api/src/opspilot/investigation/__init__.py` exports updated.
**Documentation:** `docs/architecture/domain-models.md` added; `LEARNING-NOTES.md` updated.

**Local verification, 21 Nov 2026:**

- [x] Focused tests: `python -m pytest tests/unit/test_investigation_models.py -v` — 50 passed.
- [x] Full suite: `make test` — 116 passed (66 existing + 50 new).
- [x] Ruff lint: `make lint` — passed.
- [x] Ruff format check: `make format-check` — 38 files already formatted.
- [x] Pyright: `make typecheck` — 0 errors, 0 warnings.
- [ ] User assessment: not attempted. Day 8 cannot be marked complete until the user completes and scores it.
- [ ] Hosted CI for this branch: not confirmed.
- [ ] Pull request: not created yet.

**Open catch-up items preserved:**

1. Day 2 practical evidence is unresolved.
2. Day 6 hosted post-merge CI is unconfirmed.
3. Day 7 was user-confirmed complete, but the assessment score and mock details were not supplied.

## Next step

Complete the Day 8 assessment before marking the day complete. Day 9 is type hints, generics, protocols and Pydantic; it has not been started. Keep the Day 2 practical, Day 6 hosted-CI and Day 7 assessment-detail gaps visible as catch-up items.
