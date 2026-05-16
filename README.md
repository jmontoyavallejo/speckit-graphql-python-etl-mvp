# GraphQL Python ETL Learning Platform

> Learn GraphQL by doing: master query languages, build a GraphQL server, and implement ETL pipelines—all locally, all in Python.

An interactive learning platform to master GraphQL with Python, featuring:

- **Interactive Q&A Modules**: Learn GraphQL concepts through guided question-and-answer sessions
- **Local GraphQL Server Lab**: Hands-on practice with a Strawberry GraphQL server powered by FastAPI
- **ETL Pipelines**: Real-world data engineering workflows using GraphQL as a data source
- **Progress Tracking**: Resume learning sessions seamlessly with persistent progress storage
- **Type Safety**: Strict Python 3.12 typing with `mypy --strict`
- **Comprehensive Tests**: Full test coverage with unit, integration, and contract tests

## Quick Start

See [specs/001-graphql-python-etl/quickstart.md](specs/001-graphql-python-etl/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.12+
- Ubuntu WSL2 (for Windows) or Linux
- PostgreSQL 16+ (or Docker)

### Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Running the Platform

**Terminal 1: Start GraphQL Server**
```bash
gql-learn server start
```

**Terminal 2: Start Learning Q&A**
```bash
gql-learn start
```

**Terminal 3: Run ETL Pipeline**
```bash
gql-learn pipeline run sample_library_etl
```

## Project Structure

```
src/gql_learn/          # Main package
├── cli/                # CLI commands (start, server, pipeline)
├── api/                # FastAPI application
├── gql/                # Strawberry GraphQL schema
├── db/                 # Database models and session
├── modules/            # Q&A module system
└── etl/                # ETL pipeline framework

tests/                  # Test suites
├── unit/               # Unit tests
├── integration/        # Integration tests
└── contract/           # Contract tests

data/                   # Content and seed data
├── modules/            # Q&A module JSON files
└── seed/               # Database seed scripts

specs/                  # Design documentation
├── 001-graphql-python-etl/
│   ├── spec.md         # Feature specification
│   ├── plan.md         # Implementation plan
│   ├── quickstart.md   # Setup guide
│   └── contracts/      # API contracts
```

## Development

### Running Tests

```bash
pytest --cov=src --cov-fail-under=80
```

### Linting and Formatting

```bash
ruff check src/ --fix
ruff format src/
mypy src/ --strict
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    gql-learn CLI                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Learn      │  │   Server     │  │   Pipeline   │  │
│  │   (Q&A)      │  │   (GraphQL)  │  │   (ETL)      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
└─────────┼─────────────────┼─────────────────┼──────────┘
          │                 │                 │
    ┌─────▼─────┐      ┌────▼────┐      ┌────▼────┐
    │  Modules  │      │ Strawberry│    │ ETL Core│
    │  (JSON)   │      │ FastAPI  │      │ Extract │
    │  Progress │      │ SQLAlchemy│    │Transform│
    │  (JSON)   │      └────┬─────┘     │ Load    │
    └───────────┘           │           └────┬────┘
                      ┌─────▼─────┐          │
                      │ PostgreSQL│◄─────────┘
                      │ (via DB)  │
                      └───────────┘
```

### Core Modules

- **cli/**: Command-line interface with Learn, Server, and Pipeline subcommands
- **modules/**: Q&A module loading and progress tracking
- **gql/**: Strawberry GraphQL schema and resolvers
- **etl/**: ETL pipeline extraction, transformation, and loading
- **api/**: FastAPI application and GraphQL routing

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Or use Docker
docker run --name gql-learn-db -e POSTGRES_PASSWORD=learner123 -p 5432:5432 postgres:16
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Port Already in Use
```bash
# If port 8000 is busy, kill the process
lsof -ti :8000 | xargs kill -9
```

## Command Reference

```bash
# Learning
gql-learn start              # Begin a Q&A module
gql-learn resume            # Continue from last session
gql-learn status            # Show progress summary

# GraphQL Server
gql-learn server start      # Start local GraphQL server
gql-learn server stop       # Stop the server
gql-learn server logs       # View server logs

# ETL Pipelines
gql-learn pipeline run NAME        # Execute a pipeline
gql-learn pipeline list            # Show available pipelines
gql-learn pipeline show NAME       # Display pipeline details
gql-learn pipeline runs NAME       # View execution history

# Setup
gql-learn init              # Initialize application
```

## Principles

This project follows strict principles from [.specify/memory/constitution.md](.specify/memory/constitution.md):

1. **Clean Code & Strict Typing**: Python 3.12 with `mypy --strict`
2. **Test-First Development**: 80% minimum coverage with pytest
3. **Local-Only Execution**: No cloud dependencies
4. **Clear CLI Commands**: Under 30 characters, with `--json` support
5. **Mature Dependencies**: Only stable, actively-maintained packages

## Contribution

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on development, testing, and code style.

## License

MIT
