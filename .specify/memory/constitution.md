<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Modified sections:
  - Development Workflow (expanded with uv + ruff tooling guidance)
Added tooling requirements:
  - Package Manager: uv (fast, unified dependency management)
  - Linter: ruff (unified linting + formatting, replaces black/isort/flake8)
  - Type Checker: mypy --strict (separate from ruff, for strict typing per Principle I)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section is generic)
  - .specify/templates/spec-template.md ✅ (no principle-specific references)
  - .specify/templates/tasks-template.md ✅ (no principle-specific references)
Follow-up TODOs: None
-->

# Aprender GraphQL Constitution

## Core Principles

### I. Clean Code & Strict Typing

All code MUST target Python 3.12 exclusively. Every function, method, and variable MUST carry
explicit type annotations. `mypy --strict` MUST pass with zero errors on the entire codebase.
`# type: ignore` comments are forbidden unless accompanied by a justification comment on the same
line explaining why the type system cannot express the intent.

- Use `from __future__ import annotations` at the top of every module.
- Prefer `dataclasses` or `pydantic` models over plain dicts for structured data.
- Keep functions short and single-purpose; cyclomatic complexity MUST stay ≤ 10 per function.

Rationale: strict typing eliminates entire classes of runtime bugs, improves IDE support, and makes
code self-documenting without relying on prose comments.

### II. Test-First with pytest

Tests MUST be written with pytest before any implementation code. The Red-Green-Refactor cycle is
non-negotiable: tests MUST be observed to fail before the feature is implemented. Code coverage
MUST remain at or above 80% at all times; merges below this threshold are blocked.

- Test files live under `tests/` mirroring the `src/` structure.
- Organize by scope: `tests/unit/`, `tests/integration/`, `tests/contract/`.
- Fixtures MUST be scoped appropriately (`function`/`module`/`session`) to prevent hidden state.
- Run via: `pytest --cov=src --cov-fail-under=80`

Rationale: a failing test before green code proves the test actually exercises the behavior, not
merely inflates line coverage.

### III. No Cloud — Local Execution Only

All features MUST run entirely on local hardware without network calls to cloud providers (AWS,
GCP, Azure, etc.). Cloud SDKs, managed services, and externally hosted APIs are forbidden as
dependencies. Local services (Docker containers, SQLite, local file system) are acceptable.

Rationale: local-first development removes external billing, network latency, and credential
management from the development loop, keeping the feedback cycle fast and deterministic.

### IV. Short Commands & Clear Error Messages

Every CLI entry point MUST be expressible in a single short command (≤ 30 characters including
flags). Error messages MUST answer: what went wrong, why it happened, and how to fix it. Success
output MUST be minimal and machine-parseable when piped; a `--json` flag MUST be supported
wherever the output contains structured data.

Rationale: good CLI ergonomics reduce cognitive overhead and make scripts composable with standard
shell pipelines.

### V. Mature & Maintained Dependencies Only

Third-party libraries MUST meet ALL of the following criteria before adoption:

- **Active maintenance**: a commit within the last 12 months.
- **Stable release**: semver ≥ 1.0.0.
- **Wide adoption**: ≥ 1,000 GitHub stars OR inclusion in the Python Software Foundation ecosystem.
- **Pinned versions**: declared in `pyproject.toml`; floating `*` or unbounded `>=` specifiers are
  forbidden in production dependencies.

Forbidden: abandoned packages, alpha/beta packages in production code, and packages that pull in
cloud SDKs as transitive dependencies.

Rationale: mature libraries have stable APIs, security patch cadence, and community support,
reducing supply-chain and API-stability risk.

## Development Workflow

**Git Flow Branching Model** (mandatory):
- `master` — Production-ready releases only. Tagged with semantic versions (e.g., v1.0.0).
  All commits MUST be merge commits from release branches. Never commit directly.
- `develop` — Integration branch for features. Base branch for all feature branches.
  All commits MUST come from feature branches (PRs). Never commit directly.
- `feature/<task-id>-<brief-name>` — One branch per task from `/speckit-tasks`.
  Branch from `develop`, PR back to `develop` when complete.
  Example: `feature/T001-project-setup` or `feature/001-user-auth`
- `release/v<version>` — Release branch. Created from `develop` when preparing a release.
  Only bugfixes and version bumps allowed. Merged to `master` (tagged) and back to `develop`.
- `hotfix/v<version>-<issue>` — Emergency fixes for production. Branch from `master`, merged to
  both `master` (tagged) and `develop`.

**Branch Naming**:
- Feature branches MUST reference task ID from tasks.md (e.g., `feature/T042-etl-extract`)
- Release branches: `release/v1.0.0`, `release/v1.1.0`, etc.
- Hotfix branches: `hotfix/v1.0.1-critical-bug`
- All branch names use lowercase, hyphens for spaces

**Package Management**: Use `uv` for dependency management (fast, unified tool):
- `uv sync` to install runtime + dev dependencies
- `uv sync --no-dev` for runtime only
- `uv pip install <package>` for single-package installs
- Dependencies MUST be pinned in `pyproject.toml` (Principle V)

**Code Quality Gates**: Every PR MUST:
1. Pass `ruff check src/ --fix` (unified linting + formatting per Principle I)
2. Pass `mypy src/ --strict` with zero errors (type checking)
3. Pass `pytest --cov=src --cov-fail-under=80` (test coverage, Principle II)
4. Include a changelog entry describing the user-visible change

**Tooling Details**:
- `ruff`: Replaces black, isort, flake8. Use `ruff format src/` for auto-formatting.
- `mypy`: Strict mode for type checking (separate from ruff linting).
- Pre-commit hooks (optional): Configure `.pre-commit-config.yaml` to run ruff + mypy before commits.

**Commit Strategy**:
- Feature branches: Commit frequently with descriptive messages (atomic commits per logical change).
- Main branches (`master`, `develop`): Squash-merge feature PRs to maintain linear history.
- Release branches: Preserve commit history (merge, don't squash).
- Tag all releases on `master` with semantic versions (e.g., `git tag v1.0.0`).

## Governance

This constitution supersedes all other practices and informal conventions. Amendments MUST:

1. Be proposed as a PR with a rationale section explaining the problem being solved.
2. Be reviewed by at least one other contributor (or self-approved with a documented TODO if the
   project is a solo effort).
3. Include a migration plan when the amendment breaks existing code patterns.

**Versioning policy**:
- MAJOR: removal or incompatible redefinition of a principle.
- MINOR: new principle or material expansion of existing guidance.
- PATCH: wording clarifications, typo fixes, non-semantic refinements.

All PRs and code reviews MUST verify compliance with this constitution before approval.

**Version**: 1.1.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
