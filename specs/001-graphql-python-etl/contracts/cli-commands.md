# CLI Commands Contract

**Tool**: `gql-learn` (entry point: `python -m gql_learn` or `gql-learn` if installed)

All commands MUST:
- Be ≤ 30 characters (including flags)
- Output clear, actionable error messages (Principle IV)
- Support `--help` for documentation
- Use short flags where possible

---

## Command Group: Learning (Q&A)

### `gql-learn start [OPTIONS]`

Start a new Q&A session from the first module.

**Options**:
- `--module TEXT` — Start at a specific module (e.g., `--module 02_queries`). Default: `01_schema_types`
- `--resume` — Resume last session (same as `gql-learn resume`)
- `--json` — Output responses as JSON (for scripting)

**Example**:
```bash
$ gql-learn start
Welcome to GraphQL Learning Platform
=====================================
Module: GraphQL Schema & Types

Question 1 of 5:
What is a GraphQL type?
(a) A way to define the shape of data
(b) A database table
(c) A JavaScript function

Your answer: a
✓ Correct! A GraphQL type describes...

Question 2 of 5:
...
```

**Output**:
- Interactive prompts in terminal
- Progress saved to `~/.gql-learn/progress.json` after each answer
- Exit code 0 on success, 1 on error

**Character Count**: `gql-learn start` = 15 chars ✓

---

### `gql-learn resume`

Resume the last interrupted Q&A session.

**Options**:
- `--from TEXT` — Specify which module to resume (e.g., `--from 02_queries`)
- `--json` — Output as JSON

**Example**:
```bash
$ gql-learn resume
Resuming module: GraphQL Queries (progress: 3/7 questions)

Question 4 of 7:
...
```

**Output**: Same as `start`

**Character Count**: `gql-learn resume` = 16 chars ✓

---

### `gql-learn status`

Show current learning progress.

**Options**:
- None

**Example**:
```bash
$ gql-learn status
Current Progress
================
Module: GraphQL Queries (02_queries)
  Completed: 3/7 questions
  Estimated time remaining: 8 minutes

Modules completed: 1/5 (20%)
Total score: 95/100
```

**Output**: Human-readable table; exit 0 if data exists, 1 if no progress found

**Character Count**: `gql-learn status` = 16 chars ✓

---

## Command Group: GraphQL Server

### `gql-learn server start`

Start the local GraphQL server (FastAPI + Strawberry).

**Options**:
- `--port INTEGER` — Port number (default: 8000)
- `--reload` — Auto-reload on code changes (development mode)

**Example**:
```bash
$ gql-learn server start
[Server] Starting GraphQL server...
[Server] Database: Connected to postgresql://localhost/gql_learn
[Server] Ready on http://127.0.0.1:8000
[Server]   GraphQL endpoint: http://127.0.0.1:8000/graphql
[Server]   Interactive UI: http://127.0.0.1:8000/graphql (Apollo Sandbox or similar)
[Server]   OpenAPI docs: http://127.0.0.1:8000/docs
Press Ctrl+C to stop.
```

**Output**: Logs to stdout; press Ctrl+C to stop gracefully

**Exit Code**: 0 on clean shutdown, 1 on error

**Character Count**: `gql-learn server start` = 22 chars ✓

---

### `gql-learn server stop`

Stop the running GraphQL server (via signal to process).

**Options**:
- None

**Example**:
```bash
$ gql-learn server stop
[Server] Stopping GraphQL server (PID 12345)...
[Server] Stopped
```

**Output**: Confirmation message

**Exit Code**: 0 on success, 1 if no server is running

**Character Count**: `gql-learn server stop` = 21 chars ✓

---

### `gql-learn server logs`

Show server logs (if running in background).

**Options**:
- `--tail INTEGER` — Show last N lines (default: 50)
- `--follow` — Stream new logs (like `tail -f`)

**Example**:
```bash
$ gql-learn server logs --tail 20
[10:30:45] GraphQL query executed: books(limit: 10)
[10:30:46] Resolver latency: 125ms
...
```

**Character Count**: `gql-learn server logs` = 21 chars ✓

---

## Command Group: ETL Pipelines

### `gql-learn pipeline list`

List all available ETL pipelines (built-in + user-defined).

**Options**:
- `--json` — Output as JSON (for scripting)

**Example**:
```bash
$ gql-learn pipeline list
Available ETL Pipelines
=======================
1. sample_library_etl (built-in)
   Description: Extract authors and books, aggregate by genre, load to JSON
   Extract: query { authors { id name books { title } } }
   Load destination: json:output/libraries.json

2. custom_etl (user-defined)
   Description: My custom pipeline
   ...
```

**Output**: Table format (human-readable) or JSON

**Character Count**: `gql-learn pipeline list` = 23 chars ✓

---

### `gql-learn pipeline show NAME`

Show details of a specific pipeline.

**Arguments**:
- `NAME` — Pipeline identifier (e.g., `sample_library_etl`)

**Options**:
- `--json` — Output as JSON

**Example**:
```bash
$ gql-learn pipeline show sample_library_etl
Pipeline: sample_library_etl (built-in)
Description: Extract authors and books, load to JSON
=====================================

Extract Phase:
  GraphQL Query:
    query {
      authors {
        id
        name
        books { title year genre }
      }
    }

Transform Phase:
  Function: gql_learn.etl.transforms.aggregate_by_genre
  Action: Group books by genre, add genre statistics

Load Phase:
  Destination: json:output/libraries.json
  Format: Pretty-printed JSON

Latest run:
  Status: success
  Extracted: 15 records
  Transformed: 15 records
  Loaded: 15 records
  Duration: 2.34 seconds
```

**Character Count**: `gql-learn pipeline show` = 23 chars ✓

---

### `gql-learn pipeline run NAME [OPTIONS]`

Execute an ETL pipeline.

**Arguments**:
- `NAME` — Pipeline identifier (e.g., `sample_library_etl`)

**Options**:
- `--dry-run` — Show what would be extracted/transformed without loading
- `--output TEXT` — Override load destination (e.g., `json:custom_out.json`)
- `--json` — Output as JSON (structured results)

**Example**:
```bash
$ gql-learn pipeline run sample_library_etl
[Pipeline] sample_library_etl
[Extract]  Executing GraphQL query...
[Extract]  ✓ Extracted 15 records in 250ms
[Transform] Applying transformations...
[Transform] ✓ Transformed 15 records in 120ms
[Load]      Writing to output/libraries.json...
[Load]      ✓ Loaded 15 records in 45ms

Summary:
  Status: SUCCESS
  Total duration: 415ms
  Output: output/libraries.json (3.2 KB)
```

**Output**: Progress indicator + summary; full details in `~/.gql-learn/runs/{run_id}.json`

**Exit Code**: 0 on success, 1 on failure

**Character Count**: `gql-learn pipeline run` = 22 chars ✓

---

### `gql-learn pipeline runs NAME`

Show execution history for a pipeline.

**Arguments**:
- `NAME` — Pipeline identifier

**Options**:
- `--limit INTEGER` — Show last N runs (default: 10)
- `--json` — Output as JSON

**Example**:
```bash
$ gql-learn pipeline runs sample_library_etl --limit 5
Pipeline Runs: sample_library_etl
==================================
1. [2026-05-16 10:31:02] ✓ SUCCESS (415ms) - 15 records
2. [2026-05-16 10:25:30] ✓ SUCCESS (402ms) - 15 records
3. [2026-05-16 10:20:15] ✗ FAILED (Error: malformed query) - extracted 0 records
4. [2026-05-16 10:15:45] ✓ SUCCESS (420ms) - 15 records
5. [2026-05-16 10:10:20] ✓ SUCCESS (398ms) - 15 records
```

**Character Count**: `gql-learn pipeline runs` = 23 chars ✓

---

## Command Group: Utilities

### `gql-learn init`

Initialize the project (create directories, seed database, etc.).

**Options**:
- `--db-reset` — Clear and reseed the database
- `--force` — Overwrite existing configuration

**Example**:
```bash
$ gql-learn init
[Init] Creating ~/.gql-learn/ directory...
[Init] Initializing PostgreSQL (localhost)...
[Init] Running migrations...
[Init] Seeding sample data (20 authors, 100 books)...
[Init] Creating learning modules...
[Init] ✓ Initialized successfully

Next step: gql-learn server start
```

**Character Count**: `gql-learn init` = 14 chars ✓

---

### `gql-learn eval [OPTIONS]`

Run comprehensive evaluation test (minimum 10 multichoice questions).

**Options**:
- `--topics TEXT` — Filter by topic (schema, queries, mutations, etc.)
- `--difficulty TEXT` — Filter by difficulty (beginner/intermediate/advanced)
- `--save` — Save results to `~/.gql-learn/eval_results.json`
- `--json` — Output as JSON (for scripting)

**Example**:
```bash
$ gql-learn eval
GraphQL Evaluation Test
======================

Question 1 of 12:
What is the difference between a query and a mutation?

(a) Queries read data; mutations write data
(b) No difference; they're synonyms
(c) Mutations are faster
(d) Queries require authentication

Your answer: a
✓ Correct!

[Questions 2-12...]

RESULTS
=======
Score: 10/12 (83%)

Breakdown by Topic:
  Schemas: 100% (3/3)
  Queries: 75% (3/4)
  Mutations: 100% (3/3)
  Subscriptions: 67% (2/3)
  Performance: 50% (1/2)
  Real-world scenarios: 100% (2/2)

Weak Areas Identified:
  - Query optimization
  - Subscription edge cases
  
Recommended Review: 02_queries, 04_subscriptions
```

**Output**: Interactive evaluation with real-time scoring and % breakdown by topic

**Exit Code**: 0 on completion, 1 on error

**Minimum Questions**: 10 questions guaranteed, covering:
1. Schema design and types
2. Query syntax and operations
3. Query optimization patterns
4. Mutation design patterns
5. Error handling scenarios
6. Data structure choices
7. Performance considerations
8. Python/application integration
9. Security and best practices
10. Real-world problem solving

**Character Count**: `gql-learn eval` = 14 chars ✓

---

### `gql-learn version`

Show version information.

**Example**:
```bash
$ gql-learn version
gql-learn 0.1.0
Python 3.12.0
PostgreSQL 16.1
Strawberry 0.243.0
FastAPI 0.104.1
```

**Character Count**: `gql-learn version` = 17 chars ✓

---

## Global Options (all commands)

- `--help` / `-h` — Show help message
- `--debug` — Enable debug logging
- `--config PATH` — Use custom config file (default: `~/.gql-learn/config.toml`)
- `--no-color` — Disable colored output (for CI/non-TTY)

---

## Error Messages (Principle IV: "what / why / how to fix")

All error messages follow this format:

```
Error: Database connection failed
Reason: PostgreSQL is not running on localhost:5432
Fix:    Start PostgreSQL with: docker-compose up
        Or: sudo systemctl start postgresql
See:    gql-learn init --help
```

Examples:

```
$ gql-learn pipeline run nonexistent
Error: Pipeline 'nonexistent' not found
Available pipelines: sample_library_etl
Fix:    Use `gql-learn pipeline list` to see all pipelines
```

```
$ gql-learn start --module invalid
Error: Module 'invalid' not found
Available modules: 01_schema_types, 02_queries, 03_mutations, 04_subscriptions
Fix:    Use `gql-learn start --module 01_schema_types` to start from the beginning
```

---

## Summary

All CLI commands adhere to Principle IV: commands are short (≤ 30 chars), error messages are clear and actionable, and `--json` flags provide machine-parseable output for scripting.
