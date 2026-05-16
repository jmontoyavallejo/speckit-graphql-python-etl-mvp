# REST Endpoints Contract

**Base URL**: `http://127.0.0.1:8000`

---

## GraphQL Endpoint

### `POST /graphql`

GraphQL query/mutation endpoint. Supports both GET (queries only) and POST.

**Request**:
```json
{
  "query": "{ books(limit: 5) { id title author { name } } }",
  "variables": { "limit": 5 },
  "operationName": "GetBooks"
}
```

**Success Response** (200 OK):
```json
{
  "data": {
    "books": [
      {
        "id": "1",
        "title": "Pride and Prejudice",
        "author": { "name": "Jane Austen" }
      }
    ]
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "data": null,
  "errors": [
    {
      "message": "Cannot query field 'unknown' on type 'Query'",
      "locations": [{ "line": 1, "column": 3 }],
      "extensions": { "code": "GRAPHQL_VALIDATION_FAILED" }
    }
  ]
}
```

**Content-Type**: `application/json`

**Timeout**: 10 seconds

---

## Health Check Endpoint

### `GET /health`

Returns server status.

**Success Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-05-16T10:30:45Z"
}
```

**Database Down Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "PostgreSQL connection failed",
  "timestamp": "2026-05-16T10:30:45Z"
}
```

---

## Documentation Endpoints

### `GET /docs`

Interactive Swagger UI for all endpoints.  
Generated automatically by FastAPI.

### `GET /redoc`

ReDoc documentation interface.

### `GET /openapi.json`

OpenAPI specification in JSON format.

---

## Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200  | OK | Request succeeded |
| 400  | Bad Request | Invalid GraphQL query or malformed JSON |
| 404  | Not Found | Endpoint doesn't exist |
| 500  | Internal Server Error | Unhandled exception |
| 503  | Service Unavailable | Database disconnected |

---

## Error Message Format (Principle IV)

All error responses follow the "what / why / how to fix" pattern:

```json
{
  "errors": [
    {
      "message": "Field 'author' requires an ID argument",
      "extensions": {
        "code": "GRAPHQL_VALIDATION_FAILED",
        "hint": "Use: author(id: \"1\") { name }",
        "documentation": "See /docs for schema"
      }
    }
  ]
}
```

---

## CORS Policy

- **Allowed Origins**: `http://127.0.0.1:*`, `http://localhost:*`, `file://`
- **Allowed Methods**: GET, POST, OPTIONS
- **Allowed Headers**: Content-Type, Authorization
- **Credentials**: Allowed

---

## Rate Limiting

No rate limiting for local development. Each learner is a single user on a local machine.

---

## Authentication

None for v1. All endpoints are publicly accessible on localhost.

---

## Versioning

API version is implicit (always latest). No `/v1/` prefix.

If breaking changes occur, the entire schema is updated atomically (no versioning strategy).
