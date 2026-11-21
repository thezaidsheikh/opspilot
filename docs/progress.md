# Applied AI Engineering Progress

**Curriculum authority:** the 72-day / 12-week Applied AI Engineering roadmap in the AI Engineering project. This tracker records evidence; it does not redefine the roadmap.
**Last reconciled:** 17 Nov 2026
**Current roadmap position:** Day 7 complete by user confirmation; Day 8 is next. Day 2 practical evidence and hosted Day 6 CI remain unresolved catch-up evidence.

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
| 8 | OOP, classes, inheritance, composition, dataclasses | Next roadmap day | Day 7 completion is user-confirmed. Resolve the separately recorded Day 2 practical evidence gap as catch-up; do not claim its implementation is verified until repository evidence is found or added. |

## Day 6 catch-up checklist

- [x] Missing-service JSONL line is skipped, counted, and does not prevent valid neighboring lines from processing.
- [x] Run pytest (66 passed), Ruff lint, Ruff format check (34 files), and Pyright (0 errors) as configured by GitHub Actions.
- [x] Check GitHub Actions for the merge commit; no workflow runs or status checks were returned, so hosted CI remains unconfirmed. A local pass does not establish hosted CI completion.

## Day 7 completion record

- [x] Day 7 marked complete based on the user's confirmation.
- [ ] Assessment score/results details recorded; not supplied, so the 80% phase target cannot be independently checked.
- [ ] Interview mock details recorded; not supplied.

Day 8 is the next roadmap day. Keep the Day 2 practical and Day 6 hosted-CI evidence gaps visible as catch-up; do not describe them as verified.

## Next step

Day 7 is complete by user confirmation. Day 8 is next. Preserve the Day 2 practical evidence gap and Day 6 hosted-CI status as catch-up items; do not invent a score or CI result.
