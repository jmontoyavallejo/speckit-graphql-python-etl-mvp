# Data Model: GraphQL Python ETL Learning Platform

**Date**: 2026-05-16

---

## Entities

### 1. LearningModule

A discrete topic unit containing an ordered sequence of questions.

**Fields**:
- `id` (str): Unique identifier (e.g., `"01_schema_types"`)
- `title` (str): Human-readable title (e.g., "GraphQL Schema & Types")
- `description` (str): Overview of the module's learning goals
- `questions` (list[Question]): Ordered list of questions
- `estimated_duration_minutes` (int): Rough time to complete

**Validation**:
- `questions` list MUST NOT be empty
- `estimated_duration_minutes` MUST be > 0

**Relationships**:
- One module contains many questions (1:N)

---

### 2. Question

An interactive prompt with one or more acceptable answers.

**Fields**:
- `id` (str): Unique within module (e.g., `"01_schema_types.q1"`)
- `text` (str): The question prompt
- `explanation` (str): Explanation shown after evaluation (correct or incorrect)
- `acceptable_answers` (list[str]): Acceptable answer strings (case-insensitive comparison)
- `hint` (str | None): Optional hint shown on retry
- `type` (str): Question type: `"multiple_choice"` | `"short_answer"` | `"matching"`

**Validation**:
- `text` and `explanation` MUST NOT be empty
- `acceptable_answers` list MUST contain at least 1 item
- `type` MUST be one of the allowed types

**Relationships**:
- Many questions belong to one module (N:1)

---

### 3. Author (Sample Data Entity)

Database entity representing an author in the library sample dataset.

**Database Table**: `authors`

**Fields**:
- `id` (int): Primary key (auto-incrementing)
- `name` (str): Author name, unique
- `birth_year` (int | None): Optional birth year
- `nationality` (str | None): Optional country

**Validation**:
- `name` MUST NOT be empty; MUST be ≤ 255 characters
- `birth_year` (if provided) MUST be > 1000 and < current year + 1

**Relationships**:
- One author has many books (1:N)

**Sample Data**:
```
| id | name                | birth_year | nationality |
|----|---------------------|------------|-------------|
| 1  | Jane Austen         | 1775       | United Kingdom |
| 2  | George Orwell       | 1903       | United Kingdom |
| 3  | Gabriel García Márquez | 1927    | Colombia    |
```

---

### 4. Book (Sample Data Entity)

Database entity representing a book in the library sample dataset.

**Database Table**: `books`

**Fields**:
- `id` (int): Primary key (auto-incrementing)
- `title` (str): Book title
- `author_id` (int): Foreign key to `authors.id`
- `year` (int): Publication year
- `genre` (str): Genre (e.g., "Fiction", "Science Fiction", "Mystery")
- `isbn` (str | None): Optional ISBN-13

**Validation**:
- `title` MUST NOT be empty; MUST be ≤ 255 characters
- `author_id` MUST reference a valid `authors.id`
- `year` MUST be > 1000 and ≤ current year
- `genre` MUST NOT be empty

**Relationships**:
- Many books belong to one author (N:1)

**Constraints**:
- Unique constraint on `isbn` (if not NULL)
- Foreign key: `author_id` → `authors.id` (cascade on delete)

**Sample Data**:
```
| id | title                  | author_id | year | genre            |
|----|------------------------|-----------|------|------------------|
| 1  | Pride and Prejudice    | 1         | 1813 | Romance          |
| 2  | 1984                   | 2         | 1949 | Science Fiction  |
| 3  | One Hundred Years ...  | 3         | 1967 | Magical Realism  |
```

---

### 5. ETLPipeline

Metadata for an ETL workflow.

**Fields**:
- `id` (str): Unique identifier (e.g., `"sample_library_etl"`)
- `name` (str): Human-readable name
- `description` (str): What the pipeline does
- `extract_query` (str): GraphQL query string
- `transform_function` (str): Module path to Python callable (e.g., `"gql_learn.etl.transforms.add_rating"`)
- `load_destination` (str): Target (e.g., `"json:output.json"` or `"sqlite:pipeline.db"`)
- `created_at` (datetime): When the pipeline was defined
- `is_builtin` (bool): Whether this is a built-in template

**Validation**:
- `extract_query` MUST be valid GraphQL syntax
- `load_destination` MUST specify a valid destination type (`json`, `csv`, `sqlite`)
- `transform_function` MUST reference an importable Python callable

**Relationships**:
- One pipeline has many runs (1:N)

---

### 6. PipelineRun

Record of a single execution of an ETL pipeline.

**Fields**:
- `id` (str): Unique run identifier (UUID or timestamp-based)
- `pipeline_id` (str): Reference to `ETLPipeline.id`
- `status` (str): Execution status: `"pending"` | `"running"` | `"success"` | `"failed"`
- `records_extracted` (int): Number of records returned by GraphQL query
- `records_transformed` (int): Number of records after transformation
- `records_loaded` (int): Number of records successfully written to destination
- `errors` (list[str]): List of error messages (if any)
- `started_at` (datetime): When execution began
- `completed_at` (datetime | None): When execution completed (NULL if still running)
- `duration_seconds` (float | None): Total runtime

**Validation**:
- `status` MUST be one of the allowed values
- `records_*` counts MUST be ≥ 0
- `completed_at` MUST be NULL if status is `"pending"` or `"running"`
- `duration_seconds` MUST be NULL if status is not `"success"` or `"failed"`

**Relationships**:
- Many runs belong to one pipeline (N:1)

**Example Run Result**:
```
pipeline_id: "sample_library_etl"
status: "success"
records_extracted: 15
records_transformed: 15
records_loaded: 15
started_at: 2026-05-16T10:30:45Z
completed_at: 2026-05-16T10:31:02Z
duration_seconds: 17
errors: []
```

---

### 7. ProgressSession

Stores a learner's progress through Q&A modules.

**Storage**: JSON file at `~/.gql-learn/progress.json`

**Fields**:
- `current_module` (str): Currently active module ID
- `modules` (dict[str, ModuleProgress]): Keyed by module ID

**ModuleProgress**:
- `completed` (bool): Whether all questions in this module were answered correctly
- `current_question_index` (int): Which question the learner is on (0-indexed)
- `responses` (list[QuestionResponse]): User's answers

**QuestionResponse**:
- `question_id` (str)
- `answer` (str): Submitted answer
- `is_correct` (bool): Whether it was correct
- `attempts` (int): Number of attempts on this question

**Example**:
```json
{
  "current_module": "02_queries",
  "modules": {
    "01_schema_types": {
      "completed": true,
      "current_question_index": null,
      "responses": [
        {
          "question_id": "01_schema_types.q1",
          "answer": "A type definition describes the shape of data",
          "is_correct": true,
          "attempts": 1
        }
      ]
    },
    "02_queries": {
      "completed": false,
      "current_question_index": 2,
      "responses": [
        {
          "question_id": "02_queries.q1",
          "answer": "query { books { title } }",
          "is_correct": true,
          "attempts": 1
        },
        {
          "question_id": "02_queries.q2",
          "answer": "query { books }",
          "is_correct": false,
          "attempts": 2
        }
      ]
    }
  }
}
```

---

## Database Schema (PostgreSQL)

### Authors Table
```sql
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    birth_year INT CHECK (birth_year > 1000),
    nationality VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Books Table
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    year INT NOT NULL CHECK (year > 1000),
    genre VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_author_id ON books(author_id);
CREATE INDEX idx_books_genre ON books(genre);
```

---

## Relationships Summary

```
Author (1) ──→ (N) Book
  └─ One author writes many books

LearningModule (1) ──→ (N) Question
  └─ One module contains many questions

ETLPipeline (1) ──→ (N) PipelineRun
  └─ One pipeline is executed multiple times
```

---

## Data Flow

1. **Learning Path**:  
   LearningModule → Question → (learner answers) → ProgressSession

2. **ETL Path**:  
   (learner triggers) → ETLPipeline → Extract (GraphQL query to {Author, Book}) → Transform (Python function) → Load (JSON/SQLite) → PipelineRun record

3. **GraphQL Schema**:  
   (defined in `gql_learn/gql/schema.py`) → queries/mutations map to {Author, Book} database entities
