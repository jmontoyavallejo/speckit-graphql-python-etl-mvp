# Architecture Diagrams & System Design

**Auto-Updated**: These diagrams are generated from source code structure and updated on each branch.

**Last Updated**: 2026-05-16 | **Branch**: feature/T001-project-setup

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                  GraphQL Learning Platform                        │
│                 (Runs entirely on local machine)                  │
└──────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                      CLI Entry Point                               │
│                  (src/gql_learn/cli/main.py)                       │
│  Commands: start, resume, server, pipeline, eval                  │
└────────────────────────────────────────────────────────────────────┘
    │
    ├─► Learning Module (Theoretical)
    │   └─ gql-learn start/resume/status
    │      ├─ Load module JSON
    │      ├─ Present questions
    │      ├─ Evaluate answers
    │      └─ Persist progress
    │
    ├─► GraphQL Server (Practical)
    │   └─ gql-learn server start/stop
    │      ├─ FastAPI app
    │      ├─ Strawberry GraphQL schema
    │      ├─ Query/Mutation/Subscription resolvers
    │      └─ PostgreSQL database
    │
    ├─► ETL Pipeline (Practical)
    │   └─ gql-learn pipeline run
    │      ├─ Extract: Query GraphQL server
    │      ├─ Transform: Python logic
    │      └─ Load: Write to PostgreSQL/JSON
    │
    └─► Evaluation Module (Assessment)
        └─ gql-learn eval
           ├─ Present 10+ multichoice questions
           ├─ Score responses in real-time
           └─ Display % breakdown by topic
```

---

## Data Flow: Three Learning Utilities

### 1. Theoretical Utility - Q&A Learning

```
CLI start command
    │
    ├─ Load progress.json from ~/.gql-learn/
    │
    ├─ Load module JSON from data/modules/
    │   (01_schema_types.json, 02_queries.json, etc.)
    │
    ├─ Display question to user
    │
    ├─ User submits answer
    │   │
    │   ├─ Evaluate (case-insensitive match)
    │   │
    │   ├─ Show feedback (correct/incorrect + explanation)
    │   │
    │   └─ Record response in memory
    │
    ├─ Advance to next question or show completion
    │
    └─ Save progress.json atomically
       ├─ Current module
       ├─ Progress per module
       └─ All responses with timestamps
```

### 2. Practical Utility - GraphQL Server + Queries

```
CLI server start command
    │
    ├─ Initialize PostgreSQL connection
    │   └─ Use psycopg adapter
    │
    ├─ Load SQLAlchemy models
    │   ├─ Author (20+ records pre-seeded)
    │   └─ Book (100+ records with relationships)
    │
    ├─ Start FastAPI app
    │   ├─ Register Strawberry GraphQL route
    │   ├─ Enable CORS
    │   └─ Listen on 127.0.0.1:8000
    │
    ├─ User accesses GraphQL endpoint
    │   ├─ Via browser: http://localhost:8000/graphql (GraphiQL)
    │   ├─ Via CLI: gql-learn query "{authors { name books { title } }}"
    │   └─ Via ETL: Extract step queries the same endpoint
    │
    ├─ Query execution
    │   ├─ Strawberry resolves schema
    │   ├─ SQLAlchemy queries database
    │   ├─ Return JSON response
    │   └─ Log execution time
    │
    └─ User experiments and learns through interaction
```

### 3. Practical Utility - ETL Pipelines

```
CLI pipeline run <name> command
    │
    ├─ Load pipeline definition from registry
    │
    ├─ Extract Phase
    │   ├─ Connect to GraphQL server (localhost:8000)
    │   ├─ Execute extract query via httpx client
    │   ├─ Return JSON records
    │   └─ Log record count and execution time
    │
    ├─ Transform Phase
    │   ├─ Apply Python transformation function
    │   ├─ Handle errors per record
    │   └─ Log transformation metrics
    │
    ├─ Load Phase
    │   ├─ Write to PostgreSQL (INSERT/UPDATE)
    │   ├─ Or write to JSON file in output/
    │   └─ Log load count and duration
    │
    └─ Pipeline Summary
        ├─ Total records extracted
        ├─ Total records transformed
        ├─ Total records loaded
        ├─ Total execution time
        ├─ Any errors per stage
        └─ Save run log to ~/.gql-learn/runs/
```

### 4. Evaluation Utility - Assessment

```
CLI eval command
    │
    ├─ Load evaluation question set (≥10 questions minimum)
    │   ├─ Schema design questions
    │   ├─ Query strategy questions
    │   ├─ Performance optimization
    │   ├─ Error handling scenarios
    │   ├─ Data modeling
    │   ├─ Python integration
    │   ├─ Security/best practices
    │   ├─ Advanced GraphQL features
    │   ├─ Real-world problem solving
    │   └─ Tool selection
    │
    ├─ Present question + options
    │
    ├─ User selects answer
    │   │
    │   ├─ Evaluate immediately
    │   │
    │   ├─ Show: Correct/Incorrect
    │   │
    │   ├─ Show: Explanation
    │   │
    │   └─ Record response
    │
    ├─ Repeat for all 10+ questions
    │
    └─ Display Results Summary
        ├─ Total score: X/10
        ├─ Percentage: Y%
        ├─ Breakdown by topic
        │   ├─ Schemas: 80%
        │   ├─ Queries: 90%
        │   ├─ Mutations: 70%
        │   ├─ Performance: 60%
        │   └─ etc.
        ├─ Identified weak areas
        └─ Recommended review modules
```

---

## Module Dependencies

```
gql_learn/
├── cli/
│   └── main.py
│       ├── imports: click
│       ├── imports: learn.py, server.py, pipeline.py, eval.py
│       └── delegates to: specific CLI modules
│
├── db/
│   ├── models.py (Author, Book ORM)
│   ├── session.py (async engine, SessionLocal)
│   ├── seed.py (populate initial data)
│   └── __init__.py (exports)
│
├── modules/
│   ├── schemas.py (Pydantic: LearningModule, Question, ProgressSession)
│   ├── loader.py (load JSON modules)
│   ├── progress.py (save/load progress.json)
│   ├── evaluator.py (answer evaluation logic)
│   └── __init__.py (exports)
│
├── gql/
│   ├── schema.py (Strawberry GraphQL type definitions)
│   ├── resolvers.py (Query, Mutation resolver implementations)
│   └── context.py (GraphQL request context)
│
├── api/
│   ├── app.py (FastAPI factory)
│   └── routes.py (REST endpoints + GraphQL mount point)
│
├── etl/
│   ├── models.py (ETLPipeline, PipelineRun schemas)
│   ├── extract.py (GraphQL client via httpx)
│   ├── transform.py (transformation functions)
│   └── load.py (write to destination)
│
├── config.py
│   └── Settings (environment variables: DB_URL, PORT, LOG_LEVEL)
│
└── __init__.py

data/
├── modules/ (JSON content)
│   ├── 01_schema_types.json (5 questions minimum)
│   ├── 02_queries.json (5 questions minimum)
│   ├── 03_mutations.json (5 questions minimum)
│   └── 04_subscriptions.json (5 questions minimum)
│
└── seed/
    └── library.json (20+ authors, 100+ books sample data)
```

---

## Learning Progression Map

```
User starts → gql-learn start

Module 1: GraphQL Schemas & Types
├─ Q1: What is a GraphQL type?
├─ Q2: What is a schema?
├─ ... (5+ questions)
└─ [Complete with 80%+ score]
    │
    └─► Unlock Module 2

Module 2: GraphQL Queries
├─ Q1: How to query specific fields?
├─ Q2: What is query nesting?
├─ ... (5+ questions)
└─ [Complete with 80%+ score]
    │
    └─► Unlock Module 3

Module 3: Mutations
├─ Q1: What is a mutation?
├─ Q2: How do mutations differ from queries?
├─ ... (5+ questions)
└─ [Complete with 80%+ score]
    │
    └─► Unlock Module 4

Module 4: Subscriptions
├─ Q1: What are subscriptions?
├─ ... (5+ questions)
└─ [Complete with 80%+ score]
    │
    └─► All modules complete

Evaluation Test (10+ questions)
├─ Mix of topics from all modules
├─ Real-world scenarios
├─ Performance/optimization questions
└─ Score + breakdown + weak area identification
```

---

## Database Schema

```
┌─────────────┐           ┌─────────────┐
│   authors   │ 1 ──  N   │    books    │
├─────────────┤           ├─────────────┤
│ id (PK)     │──────────▶│ id (PK)     │
│ name        │           │ title       │
│ birth_year  │           │ author_id(FK)
│ nationality │           │ year        │
│ created_at  │           │ genre       │
└─────────────┘           │ isbn        │
                          │ created_at  │
                          └─────────────┘
```

Local files (NOT in PostgreSQL):
- `~/.gql-learn/progress.json` — User's learning progress
- `~/.gql-learn/runs/*.json` — ETL pipeline execution logs
- `data/modules/*.json` — Q&A content
- `output/*.json` — ETL pipeline results

---

## CI/CD Architecture Auto-Update

On each branch commit:

1. **Code Analysis**: Parse source code structure
2. **Diagram Generation**: Update architecture.md with current structure
3. **Validation**: Ensure diagrams match actual imports and dependencies
4. **Documentation**: Generate function signatures for API contracts
5. **Reporting**: Flag drift between documentation and code

This ensures architecture.md stays synchronized with the actual codebase.
