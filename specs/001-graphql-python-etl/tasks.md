---
description: "Comprehensive task breakdown for GraphQL Python ETL Learning Platform"
---

# Tasks: GraphQL Python ETL Learning Platform

**Input**: Design documents from `/specs/001-graphql-python-etl/`

**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md

**Tests**: Test tasks are included; write tests FIRST, ensure they FAIL before implementation.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, directory structure

- [X] T001 Create project directory structure per plan.md (`src/gql_learn/`, `tests/`, `data/`)
- [X] T002 Initialize pyproject.toml with Python 3.12 and core dependencies (fastapi, strawberry, psycopg, sqlalchemy, click, pytest)
- [X] T003 [P] Create Python virtual environment and install dependencies via pip/poetry
- [X] T004 [P] Create .gitignore with Python patterns (\_\_pycache\_\_/, .venv/, \*.pyc, .env)
- [X] T005 [P] Create src/gql\_learn/\_\_init\_\_.py and subpackage markers
- [X] T006 [P] Create tests/ directory structure (unit/, integration/, contract/, conftest.py)
- [X] T007 Create .env.example with DATABASE\_URL, LOG\_LEVEL, PORT settings
- [X] T008 Create docker-compose.yml for PostgreSQL + pgAdmin (development)
- [X] T009 [P] Create src/gql\_learn/config.py with Settings class (pydantic) for DB connection, ports, log levels
- [X] T010 [P] Configure pytest in pyproject.toml: testpaths, python\_files, addopts (--cov=src, --cov-fail-under=80)
- [X] T011 [P] Create src/gql\_learn/db/session.py with SQLAlchemy async engine + session factory
- [X] T012 Create README.md with project overview and quickstart reference
- [X] T013 [P] Create requirements.txt from pyproject.toml (or pin versions manually)

**Checkpoint**: Project structure ready, all dependencies installed, pytest configured.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

⚠️ **CRITICAL**: No user story work can begin until this phase is complete.

- [X] T014 Create src/gql\_learn/db/models.py with SQLAlchemy Base class and configured type hints
- [X] T015 [P] Create Author ORM model in src/gql\_learn/db/models.py (id, name, birth\_year, nationality, created\_at)
- [X] T016 [P] Create Book ORM model in src/gql\_learn/db/models.py (id, title, author\_id, year, genre, isbn, created\_at) with FK to Author
- [X] T017 [P] Create ProgressSession pydantic model in src/gql\_learn/modules/schemas.py (current\_module, modules dict, responses list)
- [X] T018 [P] Create LearningModule pydantic model in src/gql\_learn/modules/schemas.py (id, title, description, questions list, estimated\_duration)
- [X] T019 [P] Create Question pydantic model in src/gql\_learn/modules/schemas.py (id, text, explanation, acceptable\_answers, hint, type)
- [X] T020 Create src/gql\_learn/db/seed.py script to populate initial Author + Book data (20 authors, 100 books via SQLAlchemy)
- [X] T021 Create database migration/initialization script (alembic or raw SQL DDL in src/gql\_learn/db/init.sql)
- [X] T022 Create src/gql\_learn/db/__init__.py with engine, SessionLocal exports
- [X] T023 Create src/gql\_learn/modules/loader.py with load\_module(module\_id) function reading from data/modules/ JSON
- [X] T024 Create src/gql\_learn/modules/progress.py with ProgressSession persistence (load/save from ~/.gql-learn/progress.json)
- [X] T025 Create src/gql\_learn/modules/__init__.py
- [X] T026 Create src/gql\_learn/api/__init__.py and src/gql\_learn/api/app.py with FastAPI() app factory

**Checkpoint**: Database initialized with sample data, models defined, app factory ready. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Interactive GraphQL Learning (Priority: P1)

**Goal**: Learners can follow step-by-step Q&A modules, answer questions, receive feedback, and resume progress.

**Independent Test**: A learner can run `gql-learn start`, answer all questions in module 1, and see a completion summary without any server running.

### Tests for User Story 1 (TDD - write FIRST)

- [X] T027 [P] [US1] Contract test: LearningModule can load from JSON in tests/contract/test\_modules.py
- [X] T028 [P] [US1] Contract test: Question evaluation (correct/incorrect) in tests/contract/test\_questions.py
- [X] T029 [P] [US1] Unit test: ProgressSession load/save to JSON in tests/unit/test\_progress.py
- [X] T030 [P] [US1] Unit test: answer validation (blank answers, case sensitivity) in tests/unit/test\_modules.py
- [X] T031 [P] [US1] Integration test: `gql-learn start` command loads module and presents first question in tests/integration/test\_learn\_cli.py
- [X] T032 [P] [US1] Integration test: Submitting correct answer advances to next question in tests/integration/test\_learn\_cli.py
- [X] T033 [P] [US1] Integration test: Progress persists across sessions in tests/integration/test\_learn\_cli.py

### Implementation for User Story 1

- [X] T034 [P] [US1] Create src/gql\_learn/cli/learn.py with @click.command() start(), answer parsing, feedback display
- [X] T035 [P] [US1] Create src/gql\_learn/cli/learn.py resume() command to load and continue from last session
- [X] T036 [P] [US1] Create src/gql\_learn/cli/learn.py status() command to show progress summary
- [X] T037 [US1] Implement answer evaluation logic in src/gql\_learn/modules/evaluator.py (case-insensitive, levenshtein distance tolerance)
- [X] T038 [US1] Integrate ProgressSession loading/saving into start/resume commands (src/gql\_learn/cli/learn.py)
- [X] T039 [US1] Add terminal formatting (Rich library) for Q&A display: question highlight, colored feedback (green ✓ / red ✗)
- [X] T040 [US1] Create data/modules/01\_schema\_types.json with 5 questions on GraphQL types + schemas
- [X] T041 [P] [US1] Create data/modules/02\_queries.json with 5 questions on GraphQL queries
- [X] T042 [P] [US1] Create data/modules/03\_mutations.json with 5 questions on GraphQL mutations
- [X] T043 [US1] Create data/modules/04\_subscriptions.json with 5 questions on GraphQL subscriptions (post-MVP, lower detail)
- [X] T044 [US1] Integrate module loading into CLI (src/gql\_learn/cli/learn.py loads from data/modules/)
- [X] T045 [US1] Validate 80% test coverage for modules/ + cli/learn.py

**Checkpoint**: User Story 1 fully functional. Learner can launch Q&A, answer questions, receive feedback, and resume. Tests passing.

---

## Phase 4: User Story 2 - Local GraphQL Server Lab (Priority: P2)

**Goal**: Learners start a local GraphQL server and query it hands-on.

**Independent Test**: A learner can run `gql-learn server start`, then in another terminal execute a GraphQL query via http://localhost:8000/graphql and receive a correct response, all without touching user stories 1 or 3.

### Tests for User Story 2 (TDD - write FIRST)

- [X] T046 [P] [US2] Contract test: Strawberry GraphQL schema matches contracts/graphql-schema.graphql in tests/contract/test\_graphql\_schema.py
- [X] T047 [P] [US2] Unit test: Author resolvers (books relationship) in tests/unit/test\_resolvers.py
- [X] T048 [P] [US2] Unit test: Book resolvers (author relationship) in tests/unit/test\_resolvers.py
- [X] T049 [P] [US2] Integration test: Query all authors in tests/integration/test\_graphql\_server.py
- [X] T050 [P] [US2] Integration test: Query books by genre in tests/integration/test\_graphql\_server.py
- [X] T051 [P] [US2] Integration test: Mutation addBook returns correct Book type in tests/integration/test\_graphql\_server.py
- [X] T052 [P] [US2] Integration test: Malformed query returns clear GraphQL error in tests/integration/test\_graphql\_server.py
- [X] T053 [US2] Integration test: Server starts within 10 seconds via `gql-learn server start` in tests/integration/test\_server\_cli.py

### Implementation for User Story 2

- [X] T054 [P] [US2] Create src/gql\_learn/gql/schema.py with Strawberry types (Book, Author) matching data-model.md
- [X] T055 [P] [US2] Create src/gql\_learn/gql/resolvers.py with Query resolvers (books, authors, book(id), author(id))
- [X] T056 [P] [US2] Create src/gql\_learn/gql/resolvers.py with Mutation resolvers (addBook, deleteBook, updateBook, addAuthor)
- [X] T057 [P] [US2] Create src/gql\_learn/gql/context.py with GraphQL request context (session, user, etc.)
- [X] T058 [US2] Mount Strawberry schema in FastAPI app via graphql\_app route in src/gql\_learn/api/app.py
- [X] T059 [US2] Add CORS middleware in src/gql\_learn/api/app.py (allow localhost:*)
- [X] T060 [P] [US2] Create src/gql\_learn/api/routes.py with health check endpoint (GET /health)
- [X] T061 [US2] Include health check in FastAPI app in src/gql\_learn/api/app.py
- [X] T062 [P] [US2] Create src/gql\_learn/cli/server.py with @click.command() start() (subprocess uvicorn)
- [X] T063 [P] [US2] Create src/gql\_learn/cli/server.py stop() command (signal handler)
- [X] T064 [P] [US2] Create src/gql\_learn/cli/server.py logs() command (tail logs from ~/.gql-learn/server.log)
- [X] T065 [US2] Add signal handling in src/gql\_learn/cli/server.py for clean SIGTERM shutdown
- [X] T066 [US2] Validate 80% test coverage for gql/ + api/ + cli/server.py

**Checkpoint**: User Story 2 fully functional. Server starts/stops cleanly, GraphQL queries work, error messages are clear.

---

## Phase 5: User Story 3 - ETL Pipelines with GraphQL (Priority: P3)

**Goal**: Learners build and run ETL pipelines that extract from GraphQL, transform data, and load to local storage.

**Independent Test**: A learner can run `gql-learn pipeline run sample_library_etl`, see it extract, transform, and load data, and inspect the output JSON without writing any custom pipelines.

### Tests for User Story 3 (TDD - write FIRST)

- [ ] T067 [P] [US3] Unit test: GraphQL extraction via httpx in tests/unit/test\_extract.py
- [ ] T068 [P] [US3] Unit test: Data transformation (aggregate\_by\_genre) in tests/unit/test\_transform.py
- [ ] T069 [P] [US3] Unit test: Loading to JSON file in tests/unit/test\_load.py
- [ ] T070 [P] [US3] Unit test: Loading to SQLite in tests/unit/test\_load.py
- [ ] T071 [P] [US3] Unit test: PipelineRun record creation in tests/unit/test\_pipeline\_models.py
- [ ] T072 [P] [US3] Integration test: End-to-end pipeline execution in tests/integration/test\_pipeline\_e2e.py
- [ ] T073 [P] [US3] Integration test: Error handling mid-pipeline (corrupt record) in tests/integration/test\_pipeline\_e2e.py
- [ ] T074 [US3] Integration test: `gql-learn pipeline run sample_library_etl` command in tests/integration/test\_pipeline\_cli.py

### Implementation for User Story 3

- [ ] T075 [P] [US3] Create src/gql\_learn/etl/models.py with ETLPipeline, PipelineRun pydantic models
- [ ] T076 [P] [US3] Create src/gql\_learn/etl/extract.py with extract\_graphql(endpoint, query) async function using httpx
- [ ] T077 [P] [US3] Create src/gql\_learn/etl/transform.py with example transform: aggregate\_by\_genre(records)
- [ ] T078 [P] [US3] Create src/gql\_learn/etl/load.py with load\_json(records, filepath) and load\_sqlite(records, table, db) functions
- [ ] T079 [US3] Create src/gql\_learn/etl/runner.py with execute\_pipeline(pipeline: ETLPipeline) orchestrator
- [ ] T080 [US3] Implement error handling in runner.py: catch transform errors per-record, log, continue or stop
- [ ] T081 [P] [US3] Create src/gql\_learn/cli/pipeline.py with @click.command() run(name) command
- [ ] T082 [P] [US3] Create src/gql\_learn/cli/pipeline.py list() command (show available pipelines)
- [ ] T083 [P] [US3] Create src/gql\_learn/cli/pipeline.py show(name) command (display pipeline details)
- [ ] T084 [P] [US3] Create src/gql\_learn/cli/pipeline.py runs(name) command (show execution history)
- [ ] T085 [US3] Create data/pipelines/sample\_library\_etl.json: GraphQL query, transform function, load destination
- [ ] T086 [P] [US3] Create data/pipelines/ directory and sample pipeline definitions
- [ ] T087 [US3] Integrate pipeline runner into CLI (load from data/pipelines/, execute via CLI)
- [ ] T088 [US3] Implement progress display during pipeline execution (extract phase, transform phase, load phase counts)
- [ ] T089 [US3] Implement pipeline run logging to ~/.gql-learn/runs/{run\_id}.json
- [ ] T090 [US3] Validate 80% test coverage for etl/ + cli/pipeline.py

**Checkpoint**: User Story 3 fully functional. Sample ETL pipeline runs end-to-end, data flows correctly, errors are logged.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinements, documentation, type checking, final validation

- [ ] T091 [P] Run mypy --strict on all src/ files (fix type errors per Principle I)
- [ ] T092 [P] Run pytest --cov=src --cov-fail-under=80 on entire test suite
- [ ] T093 [P] Create data/modules/00\_introduction.json (welcome + overview module)
- [ ] T094 Create src/gql\_learn/cli/main.py as top-level Click group tying all subcommands (start, server, pipeline, init, status, version)
- [ ] T095 [P] Create src/gql\_learn/cli/utils.py with helper functions (print\_error, print\_success, print\_table for Rich output)
- [ ] T096 Create src/gql\_learn/cli/init.py with init command (mkdir ~/.gql-learn, seed DB, create progress file)
- [ ] T097 [P] Create src/gql\_learn/\_\_main\_\_.py as entry point for `python -m gql\_learn` and `gql-learn` CLI
- [ ] T098 [P] Add logging setup in src/gql\_learn/config.py (log to ~/.gql-learn/app.log + stdout)
- [ ] T099 Update README.md with full setup instructions, architecture diagrams, troubleshooting
- [ ] T100 [P] Create CONTRIBUTING.md with development guidelines, testing checklist
- [ ] T101 [P] Create .pre-commit-config.yaml with mypy, black, isort, pytest hooks (optional)
- [ ] T102 Final smoke test: Run full quickstart.md scenario end-to-end (init → Q&A → server → pipeline)
- [ ] T103 [P] Update docs in specs/001-graphql-python-etl/ with final implementation notes

**Checkpoint**: All code passes type check, tests at 80%+ coverage, documentation complete, CLI fully functional.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. **BLOCKS** all user stories.
- **User Stories (Phases 3-5)**: All depend on Foundational completion.
  - US1 can start after Foundational
  - US2 can start after Foundational (independent of US1)
  - US3 can start after Foundational (depends on US2 server running)
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories. Fully independent.
- **US2 (P2)**: No dependencies on other stories. Fully independent from US1.
- **US3 (P3)**: Depends on US2 server being available as a data source. Can run after US2 is complete.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before CLI commands
- Core features before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (different files, no dependencies)
- All Foundational tasks marked [P] can run in parallel (different models/files)
- Once Foundational is complete, US1 and US2 tasks can run in parallel
  - Within US1: model/schemas + CLI commands can be parallel
  - Within US2: Strawberry types + resolvers can be parallel
  - Within US3: extract + transform + load can be parallel until runner.py orchestration
- All [P] test tasks for a story can run in parallel

---

## Parallel Example: User Story 1

**Parallel Block 1** (write tests first):

```
- T027: Contract test - LearningModule loading
- T028: Contract test - Question evaluation
- T029: Unit test - ProgressSession persistence
- T030: Unit test - answer validation
- T031-T033: Integration tests - CLI behavior
```

**Parallel Block 2** (implement):

```
- T034: learn.py start() command
- T035: learn.py resume() command
- T040-T043: Create data/modules/ JSON files
```

**Sequential**:

```
- T037: Implement evaluator.py (core logic)
- T038: Integrate progress persistence
- T039: Add Rich formatting
- T044: Integrate module loading
- T045: Verify 80% coverage
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1**: Setup ✓
2. **Complete Phase 2**: Foundational ✓ (models, database ready)
3. **Complete Phase 3**: User Story 1 (Q&A) ✓
4. **STOP and VALIDATE**: Test US1 independently
   - `gql-learn start` → answer all questions → see completion
   - Progress saved and can be resumed
5. Deploy/demo US1 as learning MVP

### Incremental Delivery

1. **Setup + Foundational + US1** → MVP (working Q&A)
2. **Add US2** → Hands-on lab (server + GraphQL)
3. **Add US3** → Data engineering (ETL pipelines)
4. **Polish & final validation**

### Parallel Team Strategy (if multiple developers)

With 1 developer:

1. Developer: Complete Setup + Foundational (serial)
2. Developer: Implement US1, US2, US3 sequentially (or US1+US2 in parallel if desired)
3. All: Polish & validation together

With 3+ developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Q&A)
   - Developer B: US2 (Server)
   - Developer C: US3 (ETL) — can start after US2 completes
3. US1 and US2 merge first; US3 follows

---

## Notes

- [P] tasks = parallelizable (different files, no internal dependencies)
- [US1]/[US2]/[US3] = maps task to user story for traceability
- Test tasks (T027-T033, etc.) are listed in execution order but MUST be written before their corresponding implementation tasks
- Each user story is independently completable and testable at its checkpoint
- See data-model.md for entity details, contracts/ for API specs, quickstart.md for integration scenarios
- Constitution compliance: All code must pass mypy --strict, pytest --cov-fail-under=80, and use Python 3.12 type annotations
