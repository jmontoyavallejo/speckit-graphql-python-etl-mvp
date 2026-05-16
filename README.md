# GraphQL Python ETL Learning Platform

An interactive learning platform to master GraphQL with Python, featuring:

- **Interactive Q&A Modules**: Learn GraphQL concepts through guided question-and-answer sessions
- **Local GraphQL Server**: Hands-on practice with a Strawberry GraphQL server powered by FastAPI
- **ETL Pipelines**: Real-world data engineering workflows using GraphQL as a data source
- **Progress Tracking**: Resume learning sessions seamlessly with persistent progress storage

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

## Principles

This project follows strict principles from [.specify/memory/constitution.md](.specify/memory/constitution.md):

1. **Clean Code & Strict Typing**: Python 3.12 with `mypy --strict`
2. **Test-First Development**: 80% minimum coverage with pytest
3. **Local-Only Execution**: No cloud dependencies
4. **Clear CLI Commands**: Under 30 characters, with `--json` support
5. **Mature Dependencies**: Only stable, actively-maintained packages

## License

MIT
