# Contributing Guide

Welcome! We're excited you're interested in contributing to the GraphQL Python ETL Learning Platform.

## Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker for local database)
- Git

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd gql-learn
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Database setup**
   ```bash
   # Using Docker
   docker run --name gql-learn-db -e POSTGRES_PASSWORD=learner123 -p 5432:5432 postgres:16
   
   # Or configure .env with your PostgreSQL connection
   DATABASE_URL=postgresql://user:password@localhost:5432/gql_learn
   ```

3. **Initialize the application**
   ```bash
   gql-learn init
   ```

## Development Workflow

### Branch Naming

Follow strict git flow naming:
```
feature/T<id>-<short-description>  # New feature
bugfix/T<id>-<short-description>   # Bug fix
docs/T<id>-<short-description>     # Documentation
```

Example: `feature/T095-cli-utils`

### Code Style

We enforce strict standards:

```bash
# Type checking (required)
mypy src/ --strict

# Formatting
ruff format src/ tests/

# Linting
ruff check src/ tests/ --fix

# All at once
pre-commit run --all-files
```

### Commit Messages

Write clear, imperative commit messages:

```
feat(T045): add progress persistence to CLI

- Save progress to ~/.gql-learn/progress.json
- Support resume from last module
- Add progress status command

Closes #45
```

Format: `<type>(T<id>): <description>`

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Testing Checklist

Before submitting a pull request, ensure:

- [ ] **Unit Tests Pass**
  ```bash
  pytest tests/unit/ -v
  ```

- [ ] **Integration Tests Pass**
  ```bash
  pytest tests/integration/ -v
  ```

- [ ] **Contract Tests Pass**
  ```bash
  pytest tests/contract/ -v
  ```

- [ ] **Coverage Meets 80% Threshold**
  ```bash
  pytest --cov=src --cov-fail-under=80
  ```

- [ ] **Type Checking Passes**
  ```bash
  mypy src/ --strict
  ```

- [ ] **Code is Formatted**
  ```bash
  ruff format src/ tests/
  ruff check src/ tests/ --fix
  ```

- [ ] **All Tests Run in Isolation**
  ```bash
  pytest --cov=src --cov-fail-under=80 --tb=short
  ```

## Test-Driven Development (TDD)

For new features, follow TDD:

1. Write tests FIRST (they should fail)
   ```bash
   pytest tests/unit/test_my_feature.py -v  # Should fail
   ```

2. Implement the feature
   ```bash
   # Add implementation in src/
   ```

3. Run tests again (they should pass)
   ```bash
   pytest tests/unit/test_my_feature.py -v  # Should pass
   ```

4. Ensure coverage meets requirements
   ```bash
   pytest --cov=src/gql_learn/my_module --cov-fail-under=80
   ```

## Architecture Guidelines

### Module Structure

```python
# Each module should have:
# 1. Type hints on all functions
from __future__ import annotations
from typing import TYPE_CHECKING

# 2. Docstrings
def my_function(param: str) -> bool:
    """Short description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass

# 3. Error handling at boundaries
# 4. Tests before implementation
```

### Async Code

- Use `async def` and `await` for database operations
- Use `asyncio.run()` only at CLI entry points
- All async functions should be tested with `@pytest.mark.asyncio`

### Database

- Use SQLAlchemy async for all database access
- Define models in `db/models.py`
- Use `select()` for queries, not `.query()`
- Always use sessions as context managers

## Documentation

Update documentation when:

- Adding new CLI commands → Update README.md
- Changing architecture → Update `specs/001-graphql-python-etl/architecture.md`
- Adding new modules → Update `specs/001-graphql-python-etl/plan.md`
- Creating features → Add tests/docs explaining the feature

## Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/T<id>-description
   ```

2. **Make your changes**
   - Write tests first
   - Implement feature
   - Ensure all checks pass

3. **Run final verification**
   ```bash
   pytest --cov=src --cov-fail-under=80
   mypy src/ --strict
   ruff check src/ tests/ --fix
   ```

4. **Create pull request**
   - Reference related issue/task
   - Describe changes clearly
   - Include testing evidence

5. **Address review feedback**
   - Make requested changes
   - Push new commits
   - Re-run tests

## Common Tasks

### Adding a New CLI Command

1. Create module in `src/gql_learn/cli/my_command.py`
2. Define Click command with `@click.command()`
3. Add to main.py: `cli.add_command(my_command)`
4. Test with: `gql-learn my-command --help`
5. Add tests to `tests/integration/test_cli.py`

### Adding a New Q&A Module

1. Create JSON in `data/modules/NN_topic.json`
2. Follow structure from existing modules
3. Test loading: `from gql_learn.modules import load_module`
4. Add integration tests to `tests/integration/test_modules.py`

### Adding Database Model

1. Define model in `src/gql_learn/db/models.py`
2. Add to GraphQL schema in `src/gql_learn/gql/schema.py`
3. Create resolver functions
4. Write contract tests in `tests/contract/test_graphql_schema.py`
5. Add integration tests in `tests/integration/test_graphql_server.py`

## Performance Considerations

- Database queries should use indexes (see models.py)
- CLI commands should complete in <5 seconds for user feedback
- ETL pipelines should handle 1000+ records
- GraphQL resolvers should batch load related data when possible

## Support

- Check existing issues/discussions first
- Ask questions in pull request comments
- Review related specs in `specs/001-graphql-python-etl/`

Thank you for contributing! 🙏
