# Implementation Plan: GraphQL Python ETL Learning Platform

**Branch**: `001-graphql-python-etl` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-graphql-python-etl/spec.md`

## Summary

A local, offline-capable CLI + web application that teaches GraphQL with Python through
interactive Q&A modules, a locally running GraphQL server with a PostgreSQL-backed sample
dataset, and ETL pipeline templates that use GraphQL as a data source. The entire stack runs
on Python 3.12 with no cloud dependencies; developed and tested on Ubuntu via WSL.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**:
- `fastapi` 0.x — Web framework + GraphQL server (justified exception; see Complexity Tracking)
- `strawberry-graphql` 0.x — GraphQL schema definition with Python type hints (justified exception)
- `uvicorn` 0.x — ASGI server (justified exception)
- `psycopg` 3.x — PostgreSQL adapter
- `sqlalchemy` 2.x — ORM for data models
- `click` 8.x — CLI framework
- `rich` 13.x — terminal output
- `pydantic` 2.x — data validation
- `pytest` 8.x + `pytest-cov` 5.x — testing
- `httpx` 0.x — GraphQL client for ETL extraction

**Storage**: PostgreSQL (local instance on WSL) + local JSON files (progress, Q&A content)

**Testing**: pytest 8.x + pytest-cov; run via `pytest --cov=src --cov-fail-under=80`

**Package Manager**: uv (fast Python package manager; replaces pip/poetry)

**Linting**: ruff (unified linter + formatter; replaces black, isort, flake8)

**Target Platform**: Ubuntu 22.04+ on Windows Subsystem for Linux (WSL2)

**Project Type**: CLI tool + local web API (FastAPI) serving GraphQL

**Performance Goals**: Q&A feedback < 2s; GraphQL queries < 1s; ETL pipelines < 60s end-to-end

**Constraints**: No cloud providers (AWS/GCP/Azure); PostgreSQL runs locally on WSL; all user data stays on-disk

**Scale/Scope**: Single learner, local machine, ~5 Q&A modules, 3 built-in ETL pipelines, ~100 sample records in DB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code & Strict Typing | ✅ PASS | Python 3.12; `from __future__ import annotations` on all modules; `mypy --strict` configured |
| II. Test-First with pytest | ✅ PASS | Tests written before implementation; coverage gate ≥ 80% enforced in CI |
| III. No Cloud | ✅ PASS | PostgreSQL runs locally on WSL; no AWS/GCP/Azure; all data stays on-disk |
| IV. Short Commands | ✅ PASS | All CLI entry points ≤ 30 chars: `gql-learn start`, `gql-learn server start`, `gql-learn pipeline run sample` |
| V. Mature Dependencies | ⚠️ EXCEPTION | `fastapi` 0.x and `strawberry-graphql` 0.x; justified in Complexity Tracking |

**Post-Phase-1 Re-Check**: To be performed after design artifacts are complete.

## Project Structure

### Documentation (this feature)

```text
specs/001-graphql-python-etl/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (entities, DB schema)
├── quickstart.md        # Phase 1 output (setup + run guide)
├── contracts/
│   ├── graphql-schema.graphql   # GraphQL schema
│   ├── rest-endpoints.md        # FastAPI endpoint contract
│   └── cli-commands.md          # CLI command interface
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
└── gql_learn/
    ├── __init__.py
    ├── config.py                # Settings: DB connection, environment
    ├── cli/
    │   ├── __init__.py
    │   ├── main.py              # Click group; entry point
    │   ├── learn.py             # Q&A learning commands
    │   ├── server.py            # FastAPI server start/stop
    │   └── pipeline.py          # ETL pipeline runner
    ├── db/
    │   ├── __init__.py
    │   ├── models.py            # SQLAlchemy ORM models (Author, Book, etc.)
    │   ├── session.py           # DB session management
    │   └── seed.py              # Populate initial sample data
    ├── modules/
    │   ├── __init__.py
    │   ├── schemas.py           # Pydantic models for Q&A (LearningModule, Question)
    │   ├── loader.py            # Load Q&A content from data/modules/
    │   └── progress.py          # Progress persistence (local JSON)
    ├── gql/
    │   ├── __init__.py
    │   ├── schema.py            # Strawberry GraphQL schema (types + resolvers)
    │   ├── resolvers.py         # Query/Mutation/Subscription resolvers
    │   └── context.py           # GraphQL request context
    ├── api/
    │   ├── __init__.py
    │   ├── app.py               # FastAPI app factory
    │   └── routes.py            # REST endpoints (GraphQL endpoint, health, etc.)
    └── etl/
        ├── __init__.py
        ├── models.py            # ETLPipeline, PipelineRun (Pydantic)
        ├── extract.py           # GraphQL extraction (httpx client)
        ├── transform.py         # Transformation callables
        └── load.py              # Load to PostgreSQL or JSON file

data/
├── modules/                     # Q&A content (JSON files)
│   ├── 01_schema_types.json
│   ├── 02_queries.json
│   ├── 03_mutations.json
│   └── 04_subscriptions.json
└── seed/
    └── library.json             # Initial sample data (Books, Authors)

tests/
├── conftest.py                  # Pytest fixtures (DB session, FastAPI client)
├── unit/
│   ├── test_modules.py          # LearningModule, Question parsing
│   ├── test_progress.py         # Progress persistence
│   ├── test_extract.py          # GraphQL extraction logic
│   ├── test_transform.py        # Data transformation
│   └── test_load.py             # PostgreSQL load operations
├── integration/
│   ├── test_graphql_server.py   # Full GraphQL schema tests
│   ├── test_api.py              # FastAPI endpoint tests
│   └── test_pipeline_e2e.py     # End-to-end ETL pipeline
└── contract/
    └── test_graphql_schema.py   # GraphQL schema contract validation

pyproject.toml                    # Poetry/pip dependencies, pytest config
.env.example                      # Environment variables template
docker-compose.yml                # PostgreSQL + pgAdmin (local dev)
```

**Structure Decision**: Single CLI + FastAPI app. Q&A runs via `gql-learn` commands (CLI).
GraphQL server and REST API run under FastAPI. ETL pipelines are orchestrated via CLI.
Database: PostgreSQL (local via docker-compose or installed on WSL).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| `fastapi` 0.x (not ≥ 1.0.0) | Industry-standard async web framework for GraphQL + REST; no 1.x release exists; widely used in production | `flask` 3.x + `flask-graphql` is available at 3.x, but async support is limited and routing is less ergonomic |
| `strawberry-graphql` 0.x (not ≥ 1.0.0) | Type-hint-first GraphQL definition directly teaches Python typing alongside GraphQL; pedagogically aligned with Principle I | `graphene` 3.x complies with Principle V but uses class-based DSL that obscures Python typing principles |
| PostgreSQL (local) | Learning project needs a realistic DB for sample data; SQLite insufficient for teaching schema design and joins | Specification originally called for SQLite; PostgreSQL adds multi-user and concurrency learning value without violating Principle III (local service) |

---

## Phase 0: Research (Outline)

The following questions are resolved via research and documented in `research.md`:

1. **PostgreSQL setup on WSL**: How to install, run, and initialize PostgreSQL locally on Ubuntu WSL; docker-compose alternative.
2. **FastAPI + Strawberry integration**: How to expose Strawberry schema via FastAPI route; CORS and ASGI considerations.
3. **ETL extraction pattern**: Best practice for querying GraphQL endpoint from within same process; connection pooling.
4. **Progress persistence**: File-based progress storage (~/.gql-learn/progress.json) with atomic writes.
5. **Sample data seeding**: DDL + sample books/authors data; reproducible initialization via SQLAlchemy.
6. **CLI + FastAPI coordination**: Starting/stopping FastAPI server from CLI subprocess; signal handling.

**Output**: `research.md` with all decisions and rationales.

---

## Phase 1: Design & Contracts

### 1. Data Model (`data-model.md`)

Extract from spec:
- **LearningModule**: topic, ordered questions, completion state
- **Question**: prompt, acceptable answers, explanation, hints
- **Author, Book**: sample schema entities (ORM models in SQLAlchemy)
- **ETLPipeline**: name, extract query, transform function, load destination
- **PipelineRun**: pipeline_id, status, record counts, errors, timestamps

### 2. Interface Contracts (`contracts/`)

**GraphQL Schema** (`graphql-schema.graphql`):
```graphql
type Query {
  books(limit: Int = 10): [Book!]!
  book(id: ID!): Book
  authors: [Author!]!
  author(id: ID!): Author
}

type Mutation {
  addBook(title: String!, authorId: ID!, year: Int!, genre: String!): Book!
  updateBook(id: ID!, title: String, year: Int, genre: String): Book
  deleteBook(id: ID!): Boolean!
}

type Subscription {
  bookAdded: Book!
}

type Book {
  id: ID!
  title: String!
  author: Author!
  year: Int!
  genre: String!
}

type Author {
  id: ID!
  name: String!
  books: [Book!]!
}
```

**REST Endpoints** (`rest-endpoints.md`):
- `POST /graphql` — GraphQL endpoint (query, mutation)
- `GET /health` — Health check
- `GET /docs` — FastAPI automatic docs (Swagger UI)

**CLI Commands** (`cli-commands.md`):
- `gql-learn start [--module N]` — Start Q&A session
- `gql-learn resume` — Resume last session
- `gql-learn server start` — Start GraphQL/FastAPI server
- `gql-learn server stop` — Stop server
- `gql-learn pipeline list` — List ETL pipelines
- `gql-learn pipeline run <name>` — Execute pipeline

### 3. Agent Context Update

Update `CLAUDE.md` to reference this plan:
```markdown
<!-- SPECKIT START -->
Implementation plan: specs/001-graphql-python-etl/plan.md
<!-- SPECKIT END -->
```

### 4. Quickstart Guide (`quickstart.md`)

Step-by-step:
1. Install Python 3.12 on WSL
2. Clone repo + install dependencies
3. Start PostgreSQL (docker-compose or native)
4. Initialize database (alembic migrate)
5. Run `gql-learn start` to begin Q&A
6. In another terminal, `gql-learn server start` to access GraphQL
7. Run sample ETL pipeline: `gql-learn pipeline run sample-library-etl`

---

## Constitution Re-Check (Post-Phase-1)

To be verified after all design artifacts are complete:
- [ ] Principle I: All modules use type annotations; mypy --strict passes
- [ ] Principle II: Test structure matches pytest organization; fixtures configured
- [ ] Principle III: PostgreSQL is local (WSL); no cloud calls; all data on-disk
- [ ] Principle IV: All CLI commands ≤ 30 chars; error messages are clear
- [ ] Principle V: Exceptions (FastAPI, Strawberry) justified and documented

---

**Next**: Phase 2 (`/speckit-tasks` command) will generate the task list based on this plan.
