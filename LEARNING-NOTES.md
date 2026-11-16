# Learning Notes — OpsPilot (AI Engineer)

**Master revision notes. GitHub is the master copy — this file lives in the OpsPilot repo so it is never lost if a local file is lost.**
**Read this file top to bottom for fast interview revision. Every new day appends a section here and updates the Overall summary at the top.**

**Plan:** 60-day plan, 12 Nov 2026 – 11 Jan 2027 (8 weeks + 5-day interview sprint). 1 hour System Design, 1 hour AI, 1 hour OpsPilot project, every day. Study starts ~06:30 IST; the day's lesson is prepared by 06:00 IST.
**Format:** 20 min concept + 40 min apply/build per hour. Every topic with an example in English / Indian English mix. Every new term in 2–3 lines with an example.
**Rule:** If a day is missed, do not double up — continue from where you left off.
**Honesty rule for interviews:** say "I studied" for concepts learned, "I implemented" only for code that exists and can be demonstrated in the repo, and "I proposed/designed" for structures not yet verified as committed.

**Source:** Days 1–5 below are from the ChatGPT learning, 2–7 Nov 2026, plus the Day 5 repository-alignment follow-up on 10 Nov 2026 (source file: `opspilot_python_day1_to_day5_FINAL.md`). The repo snapshot reviewed on 7 Nov 2026 is historical — current GitHub state is authoritative for what exists now.

---

## Overall — Ab tak kya seekha (cumulative summary)

### Python foundations — done (Days 1–5, ChatGPT)
- **Day 1:** CPython execution (source → bytecode → runtime), virtual environments, pip, project structure, `main()` + `__name__` guard, pytest smoke test, Git init/commit.
- **Day 2:** Names/objects, dynamic + strong typing, built-in types, conversion vs type hints, truthiness, operators, `==` vs `is`, strings (immutable, indexing/slicing, methods, f-strings). Practical corrected from product transformer to incident normalisation for `INC-1042`.
- **Day 3:** Lists, tuples, sets, dicts, mutability/hashability, lookup complexity, comprehensions, generator expressions/functions, `yield`, lazy vs eager, iterable vs iterator. Practical: catalog processor (`Product`, `CatalogSummary`, `filter_products()` — evidenced in repo snapshot 7 Nov) and `read_error_lines()` log streaming (teaching example, not confirmed committed).
- **Day 4:** Conditions, truthy/falsy + short-circuit, `for`/`while`/`range`, `break`/`continue`, `enumerate`/`zip`, function design, return vs print, all argument kinds (`*args`, `**kwargs`, positional-only `/`, keyword-only `*`), LEGB, `global`/`nonlocal`, stack frames, mutable-default pitfall. Practical: incident validation, severity scoring, prioritisation, `get_critical_incidents()` (proposed).
- **Day 5:** Modules vs packages, `__init__.py` + public API, absolute/relative imports, `__name__` + `python -m`, `sys.path` / `sys.modules`, import cache + side effects, circular imports, standard library, cohesion/coupling, dependency direction, modular monolith. Practical: `Incident` model + UUID helper + factory + prioritisation — first design was `core/incidents.py` + `utils/ids.py`; later repo-aligned proposal (10 Nov) is the `incidents/` package (`models.py`, `identifiers.py`, `factory.py`, `prioritization.py`, `__init__.py`, `__main__.py`). **Verified 13 Nov 2026: the `incidents/` package is committed in master (12 Nov 2026, commit `e5f58a4`) — it is no longer just a proposal.**
- **Day 6:** Exceptions (`try` / `except` / `else` / `finally`, chaining with `from exc`), the `logging` module and levels, file handling (`pathlib`, UTF-8, `with`), JSON and JSONL. Practical: robust JSONL incident-log processor in `opspilot/ingestion/` — file-level errors raise, line-level errors are skipped, logged and counted in a summary; records are a `LogRecord` dataclass, levels are normalised to upper case, extra fields are kept in `extra`; plus prompt templates in code in `opspilot/investigation/prompts.py`. Implemented on branch `learning/day-06-exceptions-logging-json`; PR #2 opened 13 Nov 2026, awaiting Zaid's review — NOT merged yet.

### System Design — overall (so far)
- **Two-tier vs three-tier:** two-tier = client talks directly to the database (simple, logic leaks into the client). Three-tier = presentation → logic → data (each tier changes independently).
- **Modular monolith vs microservices:** modular monolith = one deployment, strict module boundaries — right for a solo developer on 8 GB RAM. Microservices = separate deployments — powerful at scale, expensive in operations.
- **OpsPilot decision:** three-tier + modular monolith. Frontend Next.js, logic FastAPI, data PostgreSQL + pgvector. Split a module out only if it genuinely needs independent scaling — record that in an ADR.
- **Error handling & resilience (Day 6):** fail fast (raise) for errors you cannot recover from — missing file, not UTF-8. Skip-and-log for errors you can recover from — one bad line in a 10,000-line log. Bounded retry only for transient errors (timeout); never retry a permanent error like bad JSON.
- **Logging levels (Day 6):** DEBUG (developer detail) / INFO (normal flow) / WARNING (odd, run continues) / ERROR (failed, needs attention) / CRITICAL (cannot continue). Skipping a bad log line is a WARNING; a missing file is an ERROR.
- **Structured logging (Day 6):** logs as fields (level, service, message, time) — searchable and countable, unlike a plain sentence.

### AI — overall (so far)
- **LLM:** predicts the next most likely text. It does not know your system unless you show it.
- **Token:** ~¾ of a word (~3–4 characters). Decides cost and context limits.
- **Prompt:** instructions + context + question, in one message.
- **Grounding / RAG:** retrieve relevant documents first, then generate a cited answer from them. This is the defence against hallucination. OpsPilot's core idea.
- **Status:** the AI topics in the roadmap below are **to be learned and implemented** — they were explicitly *not* part of Days 1–5. Do not claim them as done until the day's PR is merged.
- **Structured output (Day 6):** an LLM must return JSON matching a schema, not prose — otherwise the next pipeline step cannot trust, test or cite it. Validate LLM output at the boundary like any other input; invalid output is retried once, then "I don't know".
- **Prompt templates in code (Day 6):** system prompt + builder functions in `opspilot/investigation/prompts.py`, not hardcoded strings in handlers. The grounding rule ("answer only from the evidence") is enforced in one place. Implemented on branch, PR #2 open, not merged yet.

### Key terms — sab ek jagah
| Term | 2–3 lines, example ke saath |
|---|---|
| CPython | Python's most widely used implementation, written mostly in C. Source is compiled to bytecode, then the runtime executes it. |
| Bytecode | Intermediate instructions generated from Python source, executed by the CPython runtime. |
| Virtual environment | Isolated dependencies for one project, e.g. OpsPilot's packages do not disturb system Python or another project. |
| Main guard | `if __name__ == "__main__": main()` — runs entry code only when executed directly, not on import. |
| Dynamic typing | Names bind to runtime objects; a name can be rebound to another type. Type is checked at runtime. |
| Strong typing | Incompatible operations are generally rejected, not silently coerced. Dynamic typing is a separate property. |
| `==` vs `is` | `==` = value equality. `is` = same object (identity). Use `is` for `None` checks, not as a general `==`. |
| Hashable | Stable hash + equality while stored, so it can be a dict key / set member. `list`/`dict`/`set` are unhashable. |
| Comprehension | Concise way to build a collection from an iterable, e.g. `[x for x in incidents if x["status"] == "OPEN"]`. |
| Generator / `yield` | Produces values lazily, one at a time, suspending and preserving state. Good for streaming large logs without loading them all. |
| Iterable vs iterator | Iterable can produce an iterator; iterator returns successive values with `next()` and keeps iteration state. |
| LEGB | Name lookup order: Local, Enclosing, Global, Built-in. |
| Mutable default pitfall | `def f(tags=[])` reuses the same list across calls. Use `tags=None` and create a new list inside. |
| Module vs package | Module = one `.py` file. Package = a namespace grouping modules, usually a directory with `__init__.py`. |
| `sys.path` / `sys.modules` | `sys.path` = locations searched for imports. `sys.modules` = cache of already-loaded modules. |
| Circular import | A imports B and B imports A (directly or indirectly) — a module may be only partially initialised. Fix the design, don't just patch it. |
| Cohesion / coupling | Cohesion = how closely a module's responsibilities belong together (want high). Coupling = how much modules depend on each other (want low, unnecessary coupling). |
| Modular monolith | One deployable app divided into well-defined internal modules with clear boundaries. Not "one giant file". |
| Tier | One layer with one job, e.g. the database tier only stores data. |
| LLM | Predicts the next most likely text; a well-read colleague who has never seen your system. |
| Token | ~¾ of a word; the unit LLMs read, write and charge by. |
| Prompt | Instructions + context + question, in one message. |
| Grounding | Answering only from given documents, e.g. from the actual error log, not from general knowledge. |
| RAG | Retrieve relevant docs first, then generate a cited answer from them. |
| Hallucination | A confident, fluent, wrong answer — e.g. inventing a config value that does not exist. |
| Pydantic | Python validation from type hints, like Zod for TypeScript. |
| Domain model | A class for a business concept, e.g. `Incident`, not a database row. |
| Exception | A runtime error that interrupts normal flow, e.g. a missing file or malformed JSON. |
| Fail fast | Stop loudly when recovery is impossible, e.g. missing input file → raise, don't return an empty result. |
| Graceful degradation | Keep working with reduced function, e.g. skip 3 bad lines, process the rest, report the 3. |
| Structured logging | Logs as fields (level, service, message), searchable and countable. |
| Structured output | LLM output in a fixed JSON shape matching a schema, not prose. |
| JSONL | One JSON object per line in a file, streamed lazily line by line. |
| Exception chaining | `raise NewError(...) from exc` — the new error keeps the original cause visible in the trace. |
| Prompt template | A prompt stored as a named constant / builder function in code, not a hardcoded string in a handler. |
| Bounded retry | Retrying a transient error (timeout) a fixed number of times, never forever, never for permanent errors. |
| `LogFileError` / `LogLineError` | File-level error (raise) vs line-level error (skip, log, count) in OpsPilot's ingestion. |
| `LogRecord` | One validated log record (level, service, message, line number, extra fields), returned by the Day 6 processor. |

---

## AI Roadmap — Sab important AI topics: padhna + implement karna, dono

**Ye sab Days 1–5 me nahi tha. Har topic ko pehle padhenge, phir OpsPilot me implement karenge. Koi bhi topic sirf padh ke chhodna nahi hai — har ek ka OpsPilot me ek concrete implementation target hai.**

### A. LLM fundamentals — padhna + implement karna
| Topic | Padhna (concept) | OpsPilot me implement karna |
|---|---|---|
| How an LLM works | Next-token prediction, training vs inference, context window, temperature / sampling | A small grounded Q&A helper that calls an LLM API with a fixed system prompt and returns the raw + grounded answer side by side |
| Tokens, context window, cost | Token counting, context limits, cost per 1k tokens | Token counter + cost estimator on every investigation request; truncate/ summarise when the context would overflow |
| Prompt engineering | System vs user prompts, instructions + context + question, few-shot, structured output | Prompt templates in code (not hardcoded strings in handlers) for incident summarisation and hypothesis generation, with tests |
| LLM internals (basic) | Attention / Transformers at a high level, embeddings as vectors | A one-page explainer + a tiny embedding demo (see section B) — no need to train a model |
| Structured output / JSON mode | Force the model to return valid JSON matching a Pydantic schema | Incident hypothesis returned as a validated Pydantic model, not free text; invalid output is retried / rejected |

### B. Embeddings, vector search & RAG — padhna + implement karna
| Topic | Padhna (concept) | OpsPilot me implement karna |
|---|---|---|
| Embeddings | Text → vector, similarity (cosine), why similar meaning lands nearby | Embed runbooks + past incident reports; store vectors in PostgreSQL + pgvector |
| Vector search | Top-k retrieval, similarity threshold, chunking (why and how big) | `retrieve(runbook_query)` — chunk runbooks, embed, store, retrieve top-k with scores and citations |
| RAG pipeline | Retrieve → rerank (optional) → generate with citations → "I don't know" when no evidence | End-to-end RAG for one incident type: retrieve docs, generate a cited answer, cite sources, say "I don't know" with no evidence |
| Chunking & ingestion | Document ingestion, chunk size/overlap trade-offs, metadata | Ingestion job: read docs, chunk, embed, upsert into pgvector, with an idempotent re-run |
| RAG evaluation | Faithfulness, relevance, RAGAS metrics, golden test set | A small golden set (question → expected sources) + RAGAS-style checks in CI; report faithfulness before/after a change |

### C. Agents, tools & LangGraph — padhna + implement karna
| Topic | Padhna (concept) | OpsPilot me implement karna |
|---|---|---|
| Tool calling / function calling | Model chooses a tool, tool runs, result goes back to the model | Read-only diagnostic tools: `get_logs(service, window)`, `get_metrics(service)`, `get_recent_deploys(service)` — each a typed tool with a schema |
| Agents | Plan → act → observe loop, when an agent helps vs when a fixed pipeline is better | An investigation agent that may call at most N diagnostic tools, then must produce a hypothesis with evidence |
| LangGraph | Graphs, nodes, edges, state, human-in-the-loop | Investigation workflow as a LangGraph graph: retrieve → diagnose → hypothesise → human approval gate → (remediation only after approval) |
| Human approval | Risky actions need explicit approval; read-only by default | Approval gate in the graph + UI/API: no remediation runs without a recorded approval |
| MCP (Model Context Protocol) | How tools are exposed to a model in a standard way | Expose at least one OpsPilot diagnostic tool via MCP, so the same tool works from the agent and from an external client |

### D. Production AI — padhna + implement karna
| Topic | Padhna (concept) | OpsPilot me implement karna |
|---|---|---|
| Evaluation / eval harness | Golden sets, regression evals, why evals matter more than vibes | `eval/` harness that runs the investigation pipeline on fixed incidents and records pass/fail + latency + cost |
| Observability | Traces, token/cost logging, Langfuse, OpenTelemetry, Prometheus | Langfuse tracing on every LLM call + Prometheus metrics (requests, tokens, latency, hallucination-flag rate) |
| Guardrails & safety | Prompt injection (basic), PII in logs, never commit secrets, output validation | Input/output validation on every LLM call; secrets only from env; PII redaction in logged prompts |
| Deployment | Docker, CI/CD, env config, health checks, background jobs (Redis) | Dockerfile + GitHub Actions CI (test, lint, type-check, eval smoke) + a deploy checklist; one Docker service at a time on 8 GB RAM |
| Async / HTTP clients | `async`/`await`, asyncio, concurrency, HTTP clients | Async LLM + embedding clients with timeouts and retries; background ingestion job via Redis queue |

### E. Python topics that unlock the AI work (from the Day 1–5 handbook, Section 8)
| Topic | When | OpsPilot implementation |
|---|---|---|
| Exceptions, logging, debugging, file handling, JSON | Day 6 (next) | Robust log-file processing: handle malformed JSON lines, log errors, never crash the whole run on one bad line |
| OOP, inheritance, composition, dataclasses (dedicated) | Day 8 | Refactor catalog/incident models to proper dataclasses / composition; fix `minPrice` / `catagory` naming found in the 7 Nov snapshot |
| Type hints, generics, protocols, Pydantic (dedicated) | Day 9 | Pydantic models for every API boundary: incident input, hypothesis output, tool results |
| Iterators/generators (dedicated), decorators, context managers | Day 10 | Streaming log reader as a reusable iterator; a timing/logging decorator; context managers for DB sessions |
| async/await, asyncio, concurrency, HTTP clients | Day 11 | Async clients above (section D) |
| FastAPI, PostgreSQL, Redis, Docker | After Python foundations | FastAPI app + pgvector + Redis jobs, in that order — no framework before the domain models are solid |

**AI interview line to be able to say by the end:** "I built a RAG investigation pipeline that retrieves runbooks from pgvector, generates cited hypotheses with a Pydantic-validated schema, runs read-only diagnostic tools through a LangGraph workflow with a human approval gate, and I evaluate it with a golden set and Langfuse traces — I can show the eval numbers, not just the demo."

---

## Day 1 — 2 Nov 2026 (ChatGPT): Python environment, execution model, project foundation

**Status: Studied. Practical `get_project_info()` — proposed, exact committed implementation not confirmed.**

- **Python vs CPython:** Python = language. CPython = most widely used implementation, written mostly in C. PyPy = another implementation.
- **Execution:** source → lexing/parsing/compilation → bytecode → CPython runtime / PVM → execution. "Python is interpreted" is shorthand — CPython compiles to bytecode first, it does not execute raw source line by line.
- **Interpreter vs compiler:** a compiler translates before execution; an interpreter/runtime executes. CPython uses both stages.
- **Virtual environment:** isolates dependencies per project. `python3 -m venv .venv`, `source .venv/bin/activate`, `deactivate`. Use `python -m pip` so pip runs through the selected interpreter. `pip freeze` prints versions — it is not itself a dependency strategy.
- **Project skeleton:** `src/opspilot/` (app package), `main.py` (entry point), `tests/`, `docs/`, `.gitignore`, `README.md`.
- **Main guard:** `if __name__ == "__main__": main()` — runs only when executed directly, not on import.
- **pytest smoke test:** a quick check that setup works; it does not prove business correctness. Run with `python -m pytest`.
- **Git:** `git init`, `git status`, `git add .`, `git commit -m "chore: initialize Python project"`. A commit is local history; pushing is separate.

**Interview Q&A:**
1. Q: Is Python compiled or interpreted? A: In CPython, source is compiled to bytecode and then executed by the runtime. "Interpreted" is shorthand, not the whole story.
2. Q: What is CPython? A: The most widely used Python implementation, written primarily in C.
3. Q: What is bytecode? A: An intermediate instruction representation generated from source and executed by the CPython runtime.
4. Q: Why use a virtual environment? A: To isolate project dependencies and avoid version conflicts between projects or with system Python.
5. Q: Why use `python -m pip`? A: It ensures pip runs using the selected Python interpreter.
6. Q: What does the main guard do? A: It runs entry-point code only when the module is executed directly, not when imported.
7. Q: `git add` vs `git commit`? A: `add` stages changes; `commit` records the staged snapshot in local history.
8. Q: What does a pytest smoke test prove? A: That a basic test path/setup works; not full correctness.

---

## Day 2 — 3 Nov 2026 (ChatGPT): Variables, objects, types, operators, strings

**Status: Studied. Incident normalisation practical — discussed; exact committed file path not confirmed. The first product-transformer exercise was superseded — keep it in history, do not use it as the OpsPilot practical.**

- **Names/objects:** `"CRITICAL"` is a string object; `severity` is a name bound to it. A name can be rebound (`value = 10` then `value = "ten"`) — Python is dynamically typed.
- **Dynamic vs strong typing:** dynamic = type checked at runtime. Strong = incompatible operations are generally rejected, not silently coerced. Dynamic does not mean "no types".
- **Built-in types:** `int` (error count), `float` (duration), `str` (service/incident ID), `bool` (status), `None` (missing value). `type()` = exact type; `isinstance()` = membership in a type hierarchy (generally preferred).
- **Conversion vs hints:** `int("1250")` converts at runtime and can raise `ValueError`. `count: int` is only an annotation — it does not convert anything.
- **Truthiness:** falsy = `False`, `None`, `0`/`0.0`, `""`, `[]`, `()`, `{}`, `set()`. Most other objects are truthy. If zero and missing mean different things, use explicit checks.
- **Operators:** arithmetic, comparison, logical, membership (`"payment" in "payment-api"`).
- **`==` vs `is`:** `==` = value equality. `is` = same object. `["error"] == ["error"]` is True, `is` is False. Use `is` for `None` checks.
- **Strings:** immutable sequences of Unicode. Indexing `value[0]`, slicing `value[start:stop]` (stop excluded), negative index from the end. Methods (`strip`, `lower`, `replace`, `split`, `startswith`, `find`) return new strings — they do not modify in place.
- **f-strings:** `f"{incident_id}: {service} reported {error_count} errors in {duration:.1f} minutes"`. Formatting: `{:.2f}`, `{count:,}`.

**Practical — incident normalisation for `INC-1042`:** trim whitespace, normalise ID/service/severity case, remove the thousands separator before `int()`, convert duration to `float`, produce a readable summary. This is a learning example, not a production validator — it assumes required keys exist. Validation / typed models were deliberately deferred.

**Interview Q&A:**
1. Q: What is dynamic typing? A: Names bind to runtime objects; the type is known at runtime and a name can be rebound to another type.
2. Q: Is Python strongly typed? A: Yes, in the practical sense — incompatible operations are generally rejected rather than silently coerced.
3. Q: `type()` vs `isinstance()`? A: `type()` returns the exact type; `isinstance()` checks membership in a type or its hierarchy.
4. Q: `==` vs `is`? A: Value equality vs object identity.
5. Q: Are strings mutable? A: No. String operations return new strings.
6. Q: Does a type hint convert data? A: No. It documents expected types; runtime conversion needs explicit code or a validation library.
7. Q: Why normalise incident fields? A: To avoid inconsistent casing, whitespace and numeric representations before filtering, grouping or comparing.

---

## Day 3 — 4 Nov 2026 (ChatGPT): Collections, comprehensions, generators

**Status: Studied. Catalog processor — evidenced in repo snapshot 7 Nov (`opspilot/catalog/processor.py`, `data/products.json`, `scripts/process_catalog.py`, `tests/unit/test_catalog.py`, `Product`/`CatalogSummary`, `filter_products()`). `read_error_lines()` — teaching example, not confirmed committed.**

- **List:** ordered, mutable, allows duplicates. `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `reverse`.
- **Tuple:** ordered, immutable as a container, allows duplicates. A tuple can contain a mutable list — the references cannot be reassigned, but the contained list can mutate.
- **Set:** unique hashable elements, no business ordering guarantee. Union `|`, intersection `&`, difference `-`, membership `in`. Good for deduplication.
- **Dict:** unique hashable keys → values. `d[key]` raises `KeyError` if absent; `d.get(key, default)` returns a default. Average lookup O(1).
- **Mutability/hashability:** mutable = can change after creation (list/dict/set). Hashable = stable hash + equality while stored. `str`/`int`/tuples of hashables can be keys; `list`/`dict`/`set` cannot. A tuple containing a list is not hashable.
- **Choosing:** ordered + changing → `list`. Fixed grouping → `tuple`. Unique/membership → `set`. Lookup by ID → `dict`.
- **Comprehensions:** list/dict/set, with transformation + condition. Avoid deeply nested ones — use a normal loop when clearer.
- **Generator expression vs list comprehension:** list materialises everything immediately; generator `(x*x for x in ...)` produces values lazily, single-pass, does not restart automatically.
- **`yield`:** emits a value, suspends the function, preserves local state, resumes on the next request. Calling a generator function returns a generator object — its body does not run fully at call time.
- **Iterable vs iterator vs generator:** iterable can produce an iterator (`iter()`); iterator returns values one at a time (`next()`); generator is a convenient iterator. Lazy = compute on request; eager = compute immediately.
- **Complexity (typical):** list index O(1), list search O(n), list append amortised O(1), dict/set lookup O(1) average, sorting O(n log n).
- **Catalog processor (repo-evidenced):** `Product` + `CatalogSummary` as frozen dataclasses (proposed), methods `active_products`, `products_by_category`, `find_by_id`, `unique_categories`, `products_by_tag`, `summary`, `filter_products`. Loads JSON, filters/maps, builds lookup dicts, dedupes categories with a set, aggregates summaries. Returns data — does not mix domain logic with printing. Snapshot note: the reviewed code used broad `Any` typing and field spellings `minPrice` and `catagory` — observations, not recommended naming. Fix these in the Day 8/9 refactors.
- **`read_error_lines(file_path)`:** yields only `ERROR` lines from a log file instead of loading the whole file. Why a generator: incremental processing, low memory, caller can stop early, reading/filtering separated from use.

**Interview Q&A:**
1. Q: List vs tuple? A: Both ordered. A list is mutable; a tuple is immutable as a container.
2. Q: List vs set? A: A list preserves order and allows duplicates. A set stores unique hashable elements, good for membership.
3. Q: Why must dict keys be hashable? A: Dicts use hashes to locate keys — a key needs stable hash/equality while stored.
4. Q: What is a comprehension? A: Concise syntax for building a collection from an iterable, with optional transformation/filtering.
5. Q: List comprehension vs generator expression? A: List materialises all results immediately; generator produces values lazily as requested.
6. Q: What does `yield` do? A: Emits a value and suspends the generator function while preserving local state.
7. Q: Why use a generator for logs? A: Streams records incrementally, reduces memory for large files, allows early termination.
8. Q: Iterable vs iterator? A: An iterable can produce an iterator; an iterator produces successive values with `next()` and keeps iteration state.
9. Q: How would you build an incident lookup by ID? A: A dict keyed by incident ID, after deciding how duplicate IDs are handled.
10. Q: When not to use a comprehension? A: When logic gets nested/hard to read, or side effects make a normal loop clearer.

---

## Day 4 — 5 Nov 2026 (ChatGPT): Control flow, functions, arguments, scope

**Status: Studied — senior-level deep dive, as requested. Incident logic — proposed; exact committed file not confirmed. The first lesson draft paths (`src/opspilot/incident_logic.py`, `examples/day4_demo.py`) did not match the actual repo structure — do not treat them as committed.**

- **Conditions:** `if` / `elif` / `else` — only the first matching branch runs. Severity → priority: CRITICAL → P1, HIGH → P2, else P3.
- **Short-circuit:** `A and B` — if A is falsy, B is not evaluated. `A or B` — if A is truthy, B is not evaluated. Guards lookups (`if incident and incident.get("severity") == "CRITICAL"`), but do not hide invalid data when the business rule needs an explicit error.
- **Loops:** `for` iterates an iterable; `range()` gives an integer sequence; `while` repeats while a condition holds. Use `for` for collections, `while` for state-driven repetition.
- **`break` / `continue` / `pass`:** exit the nearest loop / skip to next iteration / do-nothing placeholder.
- **`enumerate()` / `zip()`:** index + value together; corresponding values from multiple iterables. `zip()` stops at the shortest by default — mismatched lengths do not raise.
- **Function design:** one clear responsibility, explicit inputs, returns a result, avoids unrelated I/O and hidden global state. Testable boundaries.
- **Return vs print:** `return` sends a result to the caller; `print` writes human-readable output. Business logic should return data — the CLI/API layer decides how to present it.
- **Arguments:** positional (by position), keyword (by name), default (used when omitted). `*args` collects extra positionals into a tuple; `**kwargs` collects extra keywords into a dict. Positional-only `/` (before it, must be positional); keyword-only `*` (after it, must be by keyword — makes important config explicit).
- **Mutable default pitfall:** `def add_tag(tag, tags=[])` reuses the same list across calls. Safe form: `tags=None`, then create `[]` inside.
- **LEGB:** Local → Enclosing → Global → Built-in. `global` = module-level binding. `nonlocal` = enclosing function binding (not global). Prefer explicit parameters/returns over modifying global state.
- **Stack frames:** a call creates a frame (locals + execution position); it is removed on return. Explains local scope, nested calls, recursion, and stack traces.

**Practical — incident logic:** validate/inspect fields, map severity → priority, calculate severity scores, prioritise, filter by severity/status, summarise, `get_critical_incidents()`. Loop form is easier to extend with validation/logging; comprehension form is concise for a simple filter — choose by what the function must do next.

**Interview Q&A:**
1. Q: `for` vs `while`? A: `for` iterates an iterable; `while` repeats while a condition is true.
2. Q: What is short-circuit evaluation? A: In `and`/`or`, Python may skip the right-hand expression when the left side already determines the result.
3. Q: `break` vs `continue`? A: `break` exits the loop; `continue` skips to the next iteration.
4. Q: What does `enumerate()` solve? A: It gives an index and item together while iterating.
5. Q: What does `zip()` do? A: Iterates corresponding values from multiple iterables, stopping at the shortest by default.
6. Q: Parameter vs argument? A: A parameter is declared in the definition; an argument is supplied at the call site.
7. Q: `*args` vs `**kwargs`? A: `*args` collects extra positionals into a tuple; `**kwargs` collects extra keywords into a dict.
8. Q: Positional-only vs keyword-only? A: Positional-only must be supplied by position; keyword-only must be supplied by name.
9. Q: Explain LEGB. A: Local, Enclosing, Global, Built-in name lookup order.
10. Q: `global` vs `nonlocal`? A: `global` targets a module-level binding; `nonlocal` targets a binding in an enclosing function.
11. Q: Why avoid mutable defaults? A: The same object is reused across calls and can leak state between invocations.
12. Q: Why return data instead of printing inside a business function? A: It keeps the function reusable and testable across CLI, API, background-job and other callers.

---

## Day 5 — 6–7 Nov 2026 (ChatGPT): Modules, packages, imports, modular design

**Status: Studied. Two chronological designs — do not describe them as simultaneously verified. First design (`core/incidents.py` + `utils/ids.py`) was the lesson structure; later repo-aligned proposal (10 Nov, `incidents/` package) is a proposal — verify in Git history before claiming it is committed.**

- **Module vs package:** module = one `.py` file. Package = a namespace grouping modules, commonly a directory with `__init__.py`.
- **`__init__.py`:** initialises a regular package, can expose a deliberate public API (`from .models import Incident`, `__all__ = ["Incident"]`). Its top-level code runs on import — keep it lightweight, no expensive/surprising startup work. Modern Python also supports namespace packages without it, but a regular package is explicit and useful for OpsPilot.
- **Imports:** absolute (`from opspilot.incidents.models import Incident`) shows the full path and is easier across a project. Relative (`from .models import Incident`) is concise inside a package. Choose one consistent style; do not depend on the current working directory.
- **`__name__` + `python -m`:** run directly → `__name__ == "__main__"`. `python -m opspilot.main` locates and executes a module through the import system. A package can define `__main__.py` so `python -m opspilot.incidents` works.
- **`sys.path`:** locations searched by the import machinery (script location, `PYTHONPATH`, stdlib, `site-packages`). Do not keep mutating it inside app modules to fix packaging mistakes — fix the layout instead.
- **`sys.modules`:** cache of already-loaded modules. Import flow: check cache → reuse, else locate → create → execute top-level code → store in cache.
- **Import side effects:** top-level statements execute on first import. Avoid creating DB connections, network calls, or expensive model initialisation just because a module is imported.
- **Circular imports:** A imports B and B imports A — a module may be only partially initialised when the other accesses its names. Fix by moving shared models/constants to a lower-level module, clarifying ownership, reversing dependencies through an interface/protocol, or passing dependencies in. Do not solve every case with local imports — fix the design first.
- **Standard library (discussed):** `pathlib` (paths), `json` (parse/serialise), `logging` (events), `uuid` (IDs), `datetime` (timestamps), `os` (env/OS), `sys` (interpreter info), `re` (patterns), `asyncio` (later async work), `collections` (`Counter`, `defaultdict`, `deque`), `functools` (wrappers/caching where justified). Use a stdlib module when it solves a real requirement, not just because it exists.
- **Cohesion / coupling / dependency direction:** high cohesion (related responsibilities together), low unnecessary coupling, stable domain logic must not depend on entry-point/CLI/framework details. Public API = the small set of names a package intentionally exposes.
- **Modular monolith:** one deployable app with well-defined internal modules. Simpler deployment/local dev than microservices, clear boundaries, easier refactoring/testing, no unnecessary network calls. It is not "one giant file".
- **Incident package (repo-aligned proposal, 10 Nov):** `opspilot/incidents/` — `models.py` (dataclass + severity as `StrEnum`, proposed), `identifiers.py` (`uuid4` IDs), `factory.py` (controlled construction, keyword-only factory API proposed), `prioritization.py` (severity normalisation/validation + P1/P2/P3 mapping), `__init__.py` (intentional public exports), `__main__.py` (CLI entry point). Also: input normalisation, severity validation, tests for factory/model/prioritisation, preserve the existing catalog module and its tests, no unrelated infra/framework additions at this stage. `Incident` fields discussed: `id`, `service_name`, `title`, `severity`, `created_at`.

**Interview Q&A:**
1. Q: Module vs package? A: A module is a Python file; a package groups modules under a namespace.
2. Q: What does `__init__.py` do? A: It initialises a regular package and can expose a deliberate public API. Its top-level code runs when imported.
3. Q: Absolute vs relative import? A: Absolute uses the full package path; relative refers to modules relative to the current package.
4. Q: What is `sys.path`? A: The search locations used by Python's import machinery.
5. Q: What is `sys.modules`? A: The cache of modules already loaded in the current interpreter process.
6. Q: Why can imports have side effects? A: Because top-level statements execute when a module is first imported.
7. Q: What is a circular import? A: Two modules depend on each other, potentially exposing partially initialised modules and indicating poor dependency boundaries.
8. Q: How do you prevent circular imports? A: Clarify module ownership, extract shared abstractions into lower-level modules, use dependency injection/interfaces, keep dependency direction clear.
9. Q: What does `python -m` do? A: It executes a module located through Python's module/package import system.
10. Q: What is cohesion? A: How closely the responsibilities within a module belong together.
11. Q: What is coupling? A: The degree of dependency between modules. Avoid unnecessary knowledge of another module's internals.
12. Q: What is a modular monolith? A: One deployable application with clearly separated internal modules and boundaries.

---

## Day 6 — 13 Nov 2026 (Muse lesson): Exceptions, logging, debugging, file handling, JSON

**Status: Studied + implemented on branch `learning/day-06-exceptions-logging-json` — PR #2 opened 13 Nov 2026, awaiting Zaid's review, NOT merged. Do not claim it as in master until the PR is merged.**

**Repo state this lesson is built on:** OpsPilot `master` at merge commit `a90bb62` (LEARNING-NOTES.md merged in PR #1). Two 12 Nov commits are now verified in master: the `incidents/` package refactor (`e5f58a4`) and validated catalog JSON loading + CLI (`catalog/json_io.py`, `scripts/process_catalog.py`, `14f9e1c`). Day 6 builds on the catalog loader: whole-file JSON fails fast, streaming JSONL degrades gracefully — different input, different rule.

**Verified by running, 13 Nov 2026:** `pytest` 65 passed, `ruff check` clean, `ruff format --check` clean, `pyright` 0 errors (with the venv interpreter). CLI verified: sample log processes 5 of 9 lines, skips 4 with reasons, exit 0; missing file exits 2. Honest note: the branch as first pushed had 1 failing test (`test_invalid_utf8_raises_and_chains`) plus 2 unformatted files and 10 pyright errors — all fixed on the branch before review (see the UTF-8 note below).

- **Exceptions:** `try` runs the risky code; `except` handles a *specific* error type (never a bare `except:` — it hides bugs); `else` runs only if no exception happened; `finally` always runs (cleanup). `raise` creates the error; `raise ... from exc` chains it, keeping the original cause visible in the trace.
- **Two error layers (the Day 6 design decision):** file-level errors raise (`LogFileError` / `LogFileReadError` — missing file, unreadable, not UTF-8) because the run cannot start; line-level errors are skipped, logged as warnings and counted (`LogLineError` + `LogProcessingSummary`) because one bad line must never kill a 10,000-line batch. Know which input you are building for: a catalog file fails fast (a bad record means the dataset can't be trusted), a log stream degrades gracefully.
- **Logging module:** `logging.getLogger(__name__)` gives each module its own logger. Levels: DEBUG / INFO / WARNING / ERROR / CRITICAL. Library code uses `logger.warning(...)` / `logger.info(...)`, not `print()`. Only the CLI entry point configures formatting/level (`logging.basicConfig`).
- **File handling:** open with `pathlib.Path.open(encoding="utf-8")` inside `with` (closes the file even on error). Read line by line — never `read()` a huge log whole into memory. **UTF-8 gotcha, found by a failing test:** decoding happens while *reading*, not while *opening* — `open()` succeeds on a file with a bad byte, the `UnicodeDecodeError` fires mid-iteration. So the `try/except UnicodeDecodeError` must wrap the read loop, not just the `open()` call.
- **JSON / JSONL:** `json.loads()` parses one string; `json.JSONDecodeError` carries line/column for the message. JSONL = one JSON object per line, so a file streams lazily with a generator (`iter_log_records`, Day 3 `yield` applied). Each line needs `level`, `service` and `message`; `level` is normalised to upper case (`"info"` → `"INFO"`); `service`/`message` are stripped; extra fields (timestamp, request_id, runbook) are preserved in the record's `extra` dict. Skip reasons: `"Invalid JSON: ..."`, `"Expected a JSON object; found ..."`, `"Missing required field '...'"`, `"Unknown log level: ..."`, `"Field '...' must be a non-empty string"`.
- **Debugging:** read the *first* failure only, fix that, re-run. The summary counts (`total_lines`, `processed_count`, `skipped_count`, per-line reasons) are the debugging tool — check counts instead of guessing. `processed + skipped == total_lines` always holds.
- **Structured output (AI hour):** an LLM must return JSON matching a schema, not prose — code cannot reliably parse a paragraph. Validate LLM output at the boundary like any other input (same discipline as `json.loads()` + validation): invalid output is retried once, then "I don't know".
- **Prompt templates in code (AI hour):** `opspilot/investigation/prompts.py` — `SYSTEM_PROMPT` constant + `incident_summary_prompt(incident, evidence="")` builder. Prompts are versioned, reviewed and tested like code; the grounding rule lives in one place. With no evidence the prompt says so explicitly ("No evidence retrieved yet."), so the model must say "I don't know" instead of guessing.

**Practical — implemented (branch, PR #2 open):** `opspilot/ingestion/jsonl.py` (`LogRecord`, `LogFileError`/`LogFileReadError`, `LogLineError`, `LogProcessingSummary`, `iter_log_records`, `process_log_file`), `opspilot/investigation/prompts.py`, `scripts/process_incident_log.py` CLI, `data/incident-log-sample.jsonl` (9 non-blank lines: 5 good, 4 skipped — bad JSON, missing `message`, non-object, unknown level `FATAL`), 16 Day 6 tests (13 ingestion incl. sample-data test + 3 prompts). **Zaid's small task (5–10 min, his only code today):** add one test for a malformed log line with a missing `service` field — skipped, counted, good lines still processed.

**Interview Q&A:**
1. Q: Why not catch every exception and continue? A: Then a missing file looks like an empty result and a real problem hides. Raise what you cannot recover from; skip-and-log only what you can.
2. Q: When do you retry an error? A: Only transient errors — a timeout, a busy service. Never retry a permanent error like bad JSON; bound every retry, or it runs forever.
3. Q: Why structured logging instead of print? A: Logs with fields (level, service, message) can be searched, counted and alerted on. A plain sentence cannot.
4. Q: Why force an LLM to return JSON? A: Because code cannot reliably parse a paragraph. JSON with a schema can be validated, tested and passed to the next step.
5. Q: What do you do when the LLM returns invalid JSON? A: Reject it at the boundary, retry once with the schema repeated, and if it still fails, say "I don't know" instead of inventing an answer.
6. Q: How does OpsPilot handle a malformed log line? A: It is skipped, logged as a warning with its line number and reason, counted in the summary, and processing continues with the next line.
7. Q: Why does the catalog loader fail the whole file instead? A: A catalog is a complete dataset — a bad record means the data cannot be trusted as a whole. A log stream is different: one bad line does not invalidate the other 9,997.
8. Q: What does `from exc` do? A: It chains exceptions — the new, clearer error keeps the original error attached, so the stack trace still shows the real cause.
9. Q: When does a UTF-8 error actually fire when reading a file? A: While reading, not while opening — `open()` succeeds, the decode error fires mid-iteration. That is why the `try/except UnicodeDecodeError` wraps the read loop.

---

## What is confirmed vs not confirmed (repo evidence, 7 Nov snapshot)

| Work | Evidence status |
|---|---|
| Initial OpsPilot Python skeleton | Repository commit/snapshot was reviewed |
| Catalog processor and tests | Repository commit/snapshot was reviewed |
| `filter_products()` | Function was observed in repository snapshot |
| Day 2 incident transformer | Exercise direction discussed; exact committed path not confirmed |
| Day 4 `incident_logic.py` proposal | Lesson proposal; exact committed file not confirmed |
| Day 5 `core/incidents.py` + `utils/ids.py` design | Lesson structure discussed; do not infer all files were committed |
| Later `incidents/` package refactor | **Confirmed committed 12 Nov 2026 (`e5f58a4`) — verified in master 13 Nov** |
| `read_error_lines()` generator | Teaching example; exact committed file not confirmed |
| Validated catalog JSON loading + CLI (`catalog/json_io.py`, `scripts/process_catalog.py`) | **Confirmed committed 12 Nov 2026 (`14f9e1c`) — verified in master 13 Nov** |
| `LEARNING-NOTES.md` itself | **Merged 13 Nov 2026 (PR #1, merge commit `a90bb62`) — verified in master** |
| Day 6 JSONL processor + prompt templates + CLI + sample data | **Implemented on branch `learning/day-06-exceptions-logging-json`, PR #2 opened 13 Nov 2026, NOT merged — awaiting review. Tests run: 65 passed, ruff + pyright clean.** |

## Topics NOT in Days 1–5 (do not pull them in early)

Day 6: exceptions, logging, debugging, file handling, JSON — **done 13 Nov 2026 (this lesson; implementation on branch, PR #2 open, not merged)**. Day 8: OOP, inheritance, composition, dataclasses (dedicated). Day 9: type hints, generics, protocols, Pydantic (dedicated). Day 10: iterators/generators (dedicated), decorators, context managers. Day 11: async/await, asyncio, concurrency, HTTP clients. FastAPI, PostgreSQL, Redis, Docker. NumPy, ML, neural networks, Transformers, LLM internals. Prompt engineering, RAG, embeddings, vector search. Tool calling, agents, LangGraph, MCP. Evaluation, observability, cloud deployment, production AI operations.

**Next day — Day 7 (Sat 14 Nov 2026): topic NOT specified in the roadmap — the Python sequence jumps from Day 6 to Day 8 (OOP/dataclasses). Do not invent a Day 7 topic; confirm it with Zaid (or check the ChatGPT handbook) before preparing.**

---

## Active-recall checklist (tick off while revising)

**Day 1:** Python vs CPython · source → bytecode → runtime · interpreter/compiler nuance · venv create/activate/deactivate · pip + `python -m pip` · project structure + main guard · pytest smoke test · Git init/stage/commit · `get_project_info()`.
**Day 2:** names/objects · dynamic + strong typing · built-in types · `type()` vs `isinstance()` · conversion vs hints · truthy/falsy · operators · `==` vs `is` · strings, immutability, indexing/slicing · string methods + f-strings · INC-1042 transformation.
**Day 3:** list/tuple/set/dict · mutability/hashability · lookup complexity · comprehensions · eager vs lazy generators · iterable/iterator/generator · `yield` · catalog processor · `read_error_lines()`.
**Day 4:** conditions + truthiness · short-circuit · `for`/`while` · `range`/`break`/`continue`/`pass` · `enumerate`/`zip` · return vs print · all argument kinds · LEGB, `global`/`nonlocal` · stack frames · mutable defaults · incident validation/scoring/prioritisation/filtering/summary.
**Day 5:** module vs package · `__init__.py` + public exports · absolute vs relative imports · `__name__` + `python -m` · `sys.path`/`sys.modules` · import cache + side effects · circular imports · stdlib modules · cohesion/coupling · modular monolith · incident package (both designs, and which is which).
**Day 6:** `try`/`except`/`else`/`finally` · `from exc` chaining · fail fast vs skip-and-log · logging levels · structured logging · `pathlib` + `with` file handling · JSON/JSONL · UTF-8 decode fires on read, not open · generator streaming of log lines · `LogRecord` (level normalised, extra fields) · `LogFileError` vs `LogLineError` · `LogProcessingSummary` counts · structured LLM output + prompt templates in code · sample log: 5 processed, 4 skipped.

## One-minute interview explanation

"I started OpsPilot by setting up a clean Python project and learning how CPython executes source through bytecode, how virtual environments isolate dependencies, and how to run tests and manage the project with Git. I then learned Python's object model, dynamic typing, built-in data types, conversions, operators and string handling, applying those concepts to normalize incident data. Next, I used lists, tuples, sets, dictionaries and comprehensions to process structured records and build a catalog processor. I also learned generators and lazy iteration, which are useful for streaming large log files. Then I studied conditions, loops, function argument types, scope and reusable business logic for incident filtering and prioritization. Finally, I learned how to organize the code into modules and packages, how Python's import system works, how to avoid circular imports and how to keep the OpsPilot codebase modular and testable."
