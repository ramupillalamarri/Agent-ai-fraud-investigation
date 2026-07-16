# Agentic AI Framework for Autonomous Retail Fraud Investigation

A production-grade, enterprise-ready FastAPI backend skeleton built with clean architecture principles. This project is structured to scale for agentic workflows, machine learning integrations, and auditable financial/retail fraud investigations.

## Technologies Used

- **Python**: 3.12 (optimized, types-enforced)
- **Framework**: FastAPI (asynchronous, highly performant)
- **Database ORM**: SQLAlchemy 2.0 (using fully async engines and declarative mappings)
- **Migrations**: Alembic
- **Validation**: Pydantic v2 (for robust settings, schemas, and API validation)
- **Logging**: Structlog (for JSON structured logging in production and readable formatting in development)
- **Security**: JWT Authentication (placeholder skeleton provided)
- **Containerization**: Docker & Docker Compose

---

## Directory Architecture

```text
backend/
├── app/
│   ├── api/          # Route definitions, dependencies, and API versioning
│   ├── config/       # Environment variables parsing and configuration setups
│   ├── core/         # Core system helpers (configurations, logging hooks)
│   ├── database/     # DB initialization, session generator, and engine configuration
│   ├── middleware/   # Custom HTTP middlewares (CORS, Request tracing, performance metrics)
│   ├── models/       # Database entities (SQLAlchemy models)
│   ├── repositories/ # Repository pattern implementations for decoupling DB operations
│   ├── services/     # Business logic orchestrators and API layer interfaces
│   ├── schemas/      # Pydantic data serialization/deserialization schemas
│   ├── agents/       # LLM orchestrators and multi-agent retail auditing pipelines
│   ├── ml/           # Machine learning inference pipelines & fraud scoring models
│   ├── utils/        # Common utilities (crypto helpers, time formatters, etc.)
│   └── tests/        # Pytest integration/unit test suite
├── Dockerfile        # Production multi-stage Docker build
├── docker-compose.yml# Multi-service setup (App, PostgreSQL)
├── requirements.txt  # Project library dependencies
└── .env.example      # Configuration template file
```

---

## Architecture Design Patterns

1. **Clean Architecture**: Decoupling the application core (business models/services) from frameworks (FastAPI routes) and infrastructure (SQLAlchemy repositories/databases).
2. **Dependency Injection**: Route endpoints declare dependencies for services, services depend on repositories, and repositories depend on database sessions, leveraging FastAPI's built-in dependency injection framework (`Depends`).
3. **Repository Pattern**: Prevents SQLAlchemy ORM leakage into the API routes or services layer. Allows mock-based unit testing by swapping out real repositories with interfaces.
4. **Structured Logging**: Every request is assigned a unique Correlation ID, allowing logs to be traced end-to-end across asynchronous agent calls.

---

## Getting Started

### Local Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment settings:
   ```bash
   cp .env.example .env
   ```
4. Run locally via Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Setup
To run the database and backend services using Docker Compose:
```bash
docker-compose up --build
```
The application will expose the API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Running Tests

To execute the test suite:
```bash
pytest
```
