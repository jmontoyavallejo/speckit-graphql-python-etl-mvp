# Quickstart: GraphQL Python ETL Learning Platform

**Target**: Ubuntu WSL2 with Python 3.12  
**Package Manager**: uv (fast Python package manager)  
**Linter**: ruff (unified linting + formatting)

---

## Architecture Overview

### System Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    GraphQL Learning Platform                      │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐
│   Q&A CLI       │         │  FastAPI Server │
│  (gql-learn     │         │  + Strawberry   │
│   start)        │         │   GraphQL       │
└────────┬────────┘         └────────┬────────┘
         │                           │
         ├──► ~/.gql-learn/          │
         │    progress.json          │
         │                           │
         ├──────────────────────────►│ (optional: query during learning)
         │                           │
         └─────────────────┬─────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    │  (local)    │
                    │             │
                    │ Authors     │
                    │ Books       │
                    └─────────────┘

ETL Pipeline:
┌─────────┐   ┌──────────┐   ┌───────────┐   ┌───────────┐
│GraphQL  │──►│Transform │──►│  Load     │──►│ JSON/SQL  │
│Extract  │   │ (Python) │   │ (local)   │   │  Output   │
│(httpx)  │   │          │   │           │   │           │
└─────────┘   └──────────┘   └───────────┘   └───────────┘
    │                               │
    └──────────► PostgreSQL ◄───────┘
            (queries & results)
```

### Application Integration Flow

```
┌──────────────────────────────────┐
│     CLI Entry Point              │
│    (gql-learn command)           │
└────────────┬─────────────────────┘
             │
    ┌────────▼────────┬─────────────┬──────────────┐
    │                 │             │              │
┌───▼──┐         ┌────▼──┐    ┌────▼───┐    ┌────▼────┐
│start │         │server │    │pipeline│    │ init    │
│(Q&A) │         │(FastAPI)    │(ETL)   │    │(setup)  │
└───┬──┘         └────┬──┘    └────┬───┘    └────┬────┘
    │                 │            │             │
    ├─────────────────┼────────────┼─────────────┤
    │ Load modules    │ Start      │ Extract     │ Seed DB
    │ from JSON       │ GraphQL    │ via GraphQL │
    │                 │ schema     │             │
    │                 │            │             │
    └─────────────────┼────────────┼─────────────┘
                      │            │
                  ┌───▼────────────▼───┐
                  │  PostgreSQL (WSL)  │
                  │  - Authors         │
                  │  - Books           │
                  │  - Progress (opt)  │
                  └────────────────────┘
```

---

## Step-by-Step Setup

### 1. Prerequisites

**On Windows (outside WSL)**:
- Windows Subsystem for Linux 2 (WSL2) with Ubuntu 22.04 LTS installed
- VS Code Remote - WSL extension (recommended)

**Inside Ubuntu WSL**:
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Verify installations
python3.12 --version        # Python 3.12.x
psql --version              # psql (PostgreSQL) 16.x
```

### 2. Clone & Setup Repository

```bash
# Navigate to your workspace
cd ~/workspace  # or preferred location

# Clone the repository
git clone <repo-url> speckit-graphql-python-etl-mvp
cd speckit-graphql-python-etl-mvp

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (creates venv automatically)
uv sync  # installs runtime + dev dependencies
source .venv/bin/activate
```

### 3. Configure PostgreSQL (Local)

**Option A: Native PostgreSQL**

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER gql_learn WITH PASSWORD 'learner123';
CREATE DATABASE gql_learn OWNER gql_learn;
GRANT ALL PRIVILEGES ON DATABASE gql_learn TO gql_learn;
EOF

# Verify connection
psql -U gql_learn -d gql_learn -c "SELECT version();"
```

**Option B: Docker Compose** (if Docker is installed)

```bash
# Start services
docker-compose up -d postgres pgadmin

# Wait for PostgreSQL to be ready
sleep 5

# Verify
psql -h localhost -U gql_learn -d gql_learn -c "SELECT version();"
```

### 4. Initialize the Application

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Run initialization
gql-learn init

# Expected output:
# [Init] Creating ~/.gql-learn/ directory...
# [Init] Initializing PostgreSQL (localhost)...
# [Init] Running migrations...
# [Init] Seeding sample data (20 authors, 100 books)...
# [Init] ✓ Initialized successfully
```

### 5. Start the GraphQL Server

**In Terminal 1**:
```bash
source venv/bin/activate
gql-learn server start

# Expected output:
# [Server] Starting GraphQL server...
# [Server] Database: Connected to postgresql://localhost/gql_learn
# [Server] Ready on http://127.0.0.1:8000
# [Server]   GraphQL endpoint: http://127.0.0.1:8000/graphql
# [Server]   OpenAPI docs: http://127.0.0.1:8000/docs
```

### 6. Start Learning (in another Terminal)

**In Terminal 2**:
```bash
cd aprender-graphql
source venv/bin/activate
gql-learn start

# Expected output:
# Welcome to GraphQL Learning Platform
# =====================================
# Module: GraphQL Schema & Types
#
# Question 1 of 5:
# What is a GraphQL type?
# (a) A way to define the shape of data
# (b) A database table
# (c) A JavaScript function
#
# Your answer: a
# ✓ Correct! A GraphQL type describes...
```

### 7. Run an ETL Pipeline

**In Terminal 3**:
```bash
cd aprender-graphql
source venv/bin/activate
gql-learn pipeline run sample_library_etl

# Expected output:
# [Pipeline] sample_library_etl
# [Extract]  Executing GraphQL query...
# [Extract]  ✓ Extracted 15 records in 250ms
# [Transform] Applying transformations...
# [Transform] ✓ Transformed 15 records in 120ms
# [Load]      Writing to output/libraries.json...
# [Load]      ✓ Loaded 15 records in 45ms
#
# Summary:
#   Status: SUCCESS
#   Total duration: 415ms
#   Output: output/libraries.json (3.2 KB)
```

### 8. Access GraphQL Playground

Open in browser:
- **GraphQL Sandbox**: `http://localhost:8000/graphql`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Try a query:
```graphql
query {
  authors(limit: 5) {
    id
    name
    books {
      title
      year
      genre
    }
  }
}
```

---

## Directory Structure (after `gql-learn init`)

```
aprender-graphql/
├── src/
│   └── gql_learn/          # Main package
│       ├── cli/            # CLI commands
│       ├── db/             # Database models
│       ├── modules/        # Q&A modules
│       ├── server/         # GraphQL schema + resolvers
│       ├── gql/            # Strawberry GraphQL setup
│       ├── api/            # FastAPI app
│       ├── etl/            # ETL pipeline code
│       └── config.py       # Configuration
├── data/
│   ├── modules/            # Q&A content (JSON)
│   │   ├── 01_schema_types.json
│   │   ├── 02_queries.json
│   │   ├── 03_mutations.json
│   │   └── 04_subscriptions.json
│   └── seed/
│       └── library.json    # Sample data
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── contract/           # Contract tests
├── ~/.gql-learn/           # User data (auto-created)
│   ├── progress.json       # Learning progress
│   ├── config.toml         # User settings
│   └── runs/               # Pipeline run logs
├── pyproject.toml          # Dependencies
├── requirements.txt        # Pip dependencies
├── docker-compose.yml      # PostgreSQL + pgAdmin
└── README.md               # Project documentation
```

---

## Learning Paths

### Path 1: Pure Q&A Learning (No Server)

```bash
gql-learn start
# Answer questions sequentially
# Progress saved automatically
gql-learn status  # Check progress anytime
gql-learn resume  # Pick up where you left off
```

### Path 2: Q&A + Hands-On GraphQL

```bash
# Terminal 1: Start server
gql-learn server start

# Terminal 2: Start learning
gql-learn start

# Between questions, switch to Terminal 1 and test queries
# http://localhost:8000/graphql
```

### Path 3: ETL Pipeline Learning

```bash
# Terminal 1: Start server
gql-learn server start

# Terminal 2: List available pipelines
gql-learn pipeline list

# Run a built-in pipeline
gql-learn pipeline run sample_library_etl

# View results
cat output/libraries.json | python3 -m json.tool

# View run history
gql-learn pipeline runs sample_library_etl
```

---

## Troubleshooting

### PostgreSQL Connection Error

```
Error: Could not connect to PostgreSQL at localhost:5432
```

**Fix**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start it if needed
sudo systemctl start postgresql

# OR use Docker
docker-compose up -d postgres
```

### Port Already in Use (8000)

```
Error: Address already in use: ('127.0.0.1', 8000)
```

**Fix**:
```bash
# Use a different port
gql-learn server start --port 9000

# Or kill the existing process
lsof -i :8000
kill -9 <PID>
```

### Permission Denied on ~/.gql-learn/

```
Error: Permission denied: '/home/username/.gql-learn/progress.json'
```

**Fix**:
```bash
# Ensure directory is writable
chmod 755 ~/.gql-learn
chmod 644 ~/.gql-learn/progress.json

# Or recreate it
rm -rf ~/.gql-learn
gql-learn init
```

---

## Next Steps

1. **Complete Q&A modules** (`gql-learn start`)
2. **Experiment with GraphQL** via the playground
3. **Study sample ETL pipelines** (`gql-learn pipeline show sample_library_etl`)
4. **Create your own pipeline** using the template
5. **Review `/specs/001-graphql-python-etl/` docs** for detailed design

---

## Additional Resources

- **GraphQL Concept Docs**: `data/modules/` (JSON files)
- **API Schema**: `specs/001-graphql-python-etl/contracts/graphql-schema.graphql`
- **Data Model**: `specs/001-graphql-python-etl/data-model.md`
- **CLI Reference**: `specs/001-graphql-python-etl/contracts/cli-commands.md`
- **REST Endpoints**: `specs/001-graphql-python-etl/contracts/rest-endpoints.md`

---

## Support

```bash
# Help on any command
gql-learn --help
gql-learn start --help
gql-learn pipeline run --help

# Debug mode (verbose output)
gql-learn --debug start

# Version info
gql-learn version
```
