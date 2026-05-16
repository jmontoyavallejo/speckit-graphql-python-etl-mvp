# Research: GraphQL Python ETL Learning Platform

**Input**: Plan technical context requirements  
**Output**: Technology decisions with rationales and alternatives considered  
**Date**: 2026-05-16

---

## 1. PostgreSQL Setup on Ubuntu WSL

**Decision**: PostgreSQL 16 running natively on Ubuntu WSL2, initialized via docker-compose for convenience.

**Rationale**:
- Native WSL PostgreSQL provides direct `psycopg3` integration without Docker networking overhead
- Docker Compose alternative allows learners without WSL PostgreSQL installed to run `docker-compose up`
- Both paths compliant with Principle III (local service); docker-compose is explicitly listed as acceptable

**Alternatives Considered**:
- **SQLite (original spec)**: Insufficient for teaching multi-table joins, constraints, and schema design; lacks concurrency features
- **Cloud-hosted PostgreSQL (Atlas, Supabase)**: Violates Principle III (No Cloud)
- **Remote PostgreSQL VM**: Adds network dependency; violates Principle III

**Recommendation**: Support both native + docker-compose paths in quickstart.md

---

## 2. FastAPI + Strawberry GraphQL Integration

**Decision**: FastAPI 0.x web framework with Strawberry GraphQL schema; Strawberry mounted as a FastAPI route.

**Rationale**:
- FastAPI provides built-in async support, automatic OpenAPI docs, and CORS middleware
- Strawberry integrates natively with FastAPI via `from strawberry.fastapi import GraphQLRouter`
- Both frameworks emphasize Python type hints, aligning with Principle I
- Strawberry's code-first approach teaches GraphQL + Python typing simultaneously

**Integration Pattern**:
```python
# gql_learn/api/app.py
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from gql_learn.gql.schema import schema

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

**Alternatives Considered**:
- **Flask 3.x + Graphene 3.x**: Flask lacks async; Graphene uses class-based DSL (less pedagogical)
- **Django + Graphene**: Over-engineered for a learning project; Django ORM adds complexity
- **Quart (async Flask)**: Smaller ecosystem; less mature than FastAPI

**Conclusion**: FastAPI + Strawberry is the pedagogically optimal stack for teaching GraphQL + Python typing.

---

## 3. ETL Extraction Pattern: Querying GraphQL from Python

**Decision**: `httpx` async client to query the local GraphQL endpoint (same FastAPI process).

**Rationale**:
- `httpx` supports both sync and async HTTP; integrates with `asyncio`
- Allows learners to see extraction as a normal GraphQL query (vs. direct Python function calls)
- Demonstrates real-world pattern: services querying GraphQL endpoints

**Pattern**:
```python
# gql_learn/etl/extract.py
import httpx
from typing import Any

async def extract_graphql(
    endpoint: str, query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Execute GraphQL query; return data."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={"query": query, "variables": variables or {}},
        )
    return response.json()["data"]
```

**Alternatives Considered**:
- **Direct Python function calls** (strawberry client): Would not teach real-world GraphQL querying
- **Websockets for subscriptions**: Phase 1 only needs query/mutation; subscriptions are post-MVP
- **Connection pooling (pgbouncer)**: Not needed for single-learner, local project

**Conclusion**: httpx provides a realistic extraction pattern without over-engineering.

---

## 4. Progress Persistence: Session State Storage

**Decision**: JSON file stored at `~/.gql-learn/progress.json`; atomic writes via `json.dump` with `mode='w'`.

**Rationale**:
- File-based storage keeps data on-disk (compliant with Principle III)
- No additional DB schema needed for session state
- Learner can inspect progress file directly (transparency)
- Atomic writes prevent partial/corrupted state on crash

**Structure**:
```json
{
  "current_module": "02_queries",
  "modules": {
    "01_schema_types": { "completed": true, "score": 100 },
    "02_queries": { "completed": false, "current_question": 3, "answers": [...] }
  }
}
```

**Alternatives Considered**:
- **PostgreSQL for progress**: Over-normalized; introduces DB I/O on every answer
- **In-memory only**: Progress lost on session restart (violates spec)
- **SQLite**: Adds another dependency; JSON is sufficient for single-learner

**Conclusion**: File-based JSON is lightweight and transparent.

---

## 5. Sample Data Seeding: Library Schema + Initial Data

**Decision**: SQLAlchemy ORM models (Author, Book) with `seed.py` script populating 20-30 sample records.

**Rationale**:
- SQLAlchemy models teach ORM relationships alongside GraphQL schema design
- `seed.py` (idempotent via delete-then-insert) ensures reproducible state
- Learning value: contrast between DB schema and GraphQL schema

**Schema** (SQLAlchemy):
```python
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    year: Mapped[int]
    genre: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")
```

**Alternatives Considered**:
- **Raw SQL**: No learning value for ORMs
- **CSV import**: Harder for learners to modify data mid-session
- **Faker-generated data**: Overkill; 20 hardcoded records sufficient

**Conclusion**: SQLAlchemy + seed script provides realistic ORM learning.

---

## 6. Package Management & Linting: uv + ruff

**Decision**: Use **uv** for package management and **ruff** for linting/formatting.

**Rationale**:
- `uv`: Extremely fast (~10-100x faster than pip), written in Rust, single tool for dependency resolution and installation. Perfect for WSL development with quick feedback loops.
- `ruff`: Unified linter combining black (formatter), isort (import sorting), and flake8 (linting). Single tool, single config, ~100x faster than separate tools. Aligns with Principle I (Clean Code) by enforcing consistent style.
- Together: Reduces tool bloat, speeds up CI/CD, improves developer experience.

**Integration**:
- `pyproject.toml` defines all dependencies (runtime + dev) with clear separation
- `uv sync` replaces `pip install` (installs all deps + dev deps)
- `uv pip install` for single packages if needed
- `ruff check src/ --fix` for linting (auto-fixes where possible)
- `ruff format src/` for formatting
- `mypy src/ --strict` runs separately for type checking (stricter than ruff)

**Alternatives Considered**:
- **Poetry**: Feature-rich but slower; uv provides same functionality faster
- **pip-tools**: Older, slower; uv handles constraints natively
- **separate black/isort/flake8**: Multiple tools, multiple configs; ruff unifies all three

---

## 7. CLI + FastAPI Coordination: Starting/Stopping the Server

**Decision**: FastAPI server runs as a subprocess spawned by `gql-learn server start`; signal handling (SIGTERM) for clean shutdown.

**Rationale**:
- Subprocess approach allows CLI and server to run independently in separate terminals
- Click's `Context.call_on_close()` ensures cleanup on exit
- Signal handlers prevent orphaned processes

**Implementation**:
```python
# gql_learn/cli/server.py
import subprocess
import signal
import time

@click.command()
def start():
    """Start the GraphQL server."""
    proc = subprocess.Popen(
        ["uvicorn", "gql_learn.api.app:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    click.echo(f"[Server] PID {proc.pid} started on http://127.0.0.1:8000/graphql")
    
    def handle_interrupt(sig, frame):
        proc.terminate()
        proc.wait(timeout=5)
        click.echo("[Server] stopped")
    
    signal.signal(signal.SIGINT, handle_interrupt)
    proc.wait()
```

**Alternatives Considered**:
- **In-process server** (FastAPI running in same process): Blocks CLI; learners can't run CLI commands while server is active
- **Systemd service**: Over-engineered; requires system-level changes
- **Process manager (Supervisor)**: Adds dependency; subprocess is simpler

**Conclusion**: Subprocess + signal handling balances simplicity and control.

---

## Summary of Technology Decisions

| Component | Choice | Principle | Notes |
|-----------|--------|-----------|-------|
| Language | Python 3.12 | I | Mandatory per constitution |
| Framework | FastAPI 0.x | IV | Async, CORS, docs built-in |
| GraphQL | Strawberry 0.x | I | Code-first, type-hint-aligned |
| Database | PostgreSQL (local) | III | Local service; supports complex schemas |
| ORM | SQLAlchemy 2.x | I | Type-annotated models; industry standard |
| CLI | Click 8.x | IV | Mature, ≥ 1.0.0 |
| Terminal | Rich 13.x | IV | Colors, tables, progress bars |
| Validation | Pydantic 2.x | I | Type-based; integrates with FastAPI |
| Testing | pytest 8.x + pytest-cov 5.x | II | TDD-first; 80% coverage gate |
| HTTP Client | httpx 0.x | — | Async; realistic GraphQL extraction pattern |
| Progress Store | File (JSON) | III | On-disk; transparent; no extra DB |
| Server Config | uvicorn 0.x | — | ASGI server for FastAPI |
| Platform | Ubuntu WSL2 | — | Linux environment; reproducible |

---

## Constitution Compliance

**Principle V Exception Justification**:
- `fastapi` (0.x): No 1.x release exists; industry standard; essential for async web framework role
- `strawberry-graphql` (0.x): No 1.x release exists; pedagogically superior for teaching type-first GraphQL
- Both widely adopted (> 10k GitHub stars) and actively maintained (commits within last month)

All other dependencies meet Principle V criteria (≥ 1.0.0, active maintenance, 1k+ stars).
