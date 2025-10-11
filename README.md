# Payroll Extract API

Smart, modular service to extract payroll records and expose them through a small FastAPI application.

This repository contains:

- A refactored `modules/payroll-extract` package with standalone parsers, exporters and repositories for offline processing and examples (CSV, JSON, PDF, SQLite sample files).
- An API implemented under `app/` which exposes simple endpoints to register and list payroll records and to integrate the extraction pipeline programmatically.

## Key concepts

- The domain model is defined in `app/core/entities/payroll.py` (Pydantic `Payroll` model).
- Business logic is implemented in use-cases and a service layer (`app/core/use_cases`, `app/application/payroll_service.py`).
- Persistence is handled by the Prisma client wrapper in `app/infrastructure/database/prisma_client.py` and repository implementations under `app/infrastructure/database`.
- The HTTP API lives in `app/api/v1/routers/payroll_router.py` and is mounted by `app/main.py`.

## API

Base URL (default): http://0.0.0.0:8000

Endpoints:

- POST /payrolls/

  - Description: Register a payroll record. The endpoint validates and stores the given payroll using the application service.
  - Request body: `Payroll` model (see example below)
  - Response: The persisted `Payroll` object (with `id` and `createdAt` populated)

- GET /payrolls/
  - Description: List all payroll records persisted in the repository.
  - Response: List[Payroll]

Sample `Payroll` JSON payload:

{
"employee": "JOHN DOE",
"position": "Senior Developer",
"gross_value": 8500.0,
"net_value": 6800.0,
"month_year": "09/2025"
}

You can also open the automatic OpenAPI docs at `/docs` or `/redoc` once the app is running.

## Run the API (development)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the FastAPI app (development mode, reload enabled by default in `app/config.py`):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Notes:

- The application uses `app/config.py` (Pydantic Settings). Default values create `logs/` and `exports/` directories automatically.
- Database URL is configured via the `database_url` setting and defaults to a local Prisma SQLite file in `prisma/data.db`.

## Running the extraction module (examples)

The `modules/payroll-extract` package contains extraction examples and helper scripts for offline processing (CSV/JSON exporters, PDF text parsers and a SQLite example repository). See `modules/payroll-extract/README.md` for module-specific usage and example files (PDF, CSV and JSON sample files are included).

## Configuration

All runtime options are centralized in `app/config.py` using Pydantic `BaseSettings`. You can override settings via environment variables or an `.env` file placed at the repository root. Important settings:

- `DATABASE_URL` (or `database_url` in code) – Prisma/SQLite connection string (default: `file:<project_root>/prisma/data.db`)
- `HOST` / `PORT` – HTTP server binding
- `LOG_LEVEL` – Logging verbosity
- `EXPORT_DIR` – Directory where exporters write CSV/JSON output

Example `.env` (optional):

DATABASE_URL=file:/absolute/path/to/prisma/data.db
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

## Development notes

- The project uses Prisma for database access; the Prisma client is wrapped inside `app/infrastructure/database/prisma_client.py`.
- Dependency injection is wired in `app/container.py`. The router depends on `get_payroll_service` which resolves the service and its use case.
- Pydantic models are used for request/response validation.

## Examples

Register a payroll using curl:

```bash
curl -X POST "http://localhost:8000/payrolls/" \
  -H "Content-Type: application/json" \
  -d '{"employee":"JOHN DOE","position":"Senior Developer","gross_value":8500,"net_value":6800,"month_year":"09/2025"}'
```

List payrolls:

```bash
curl http://localhost:8000/payrolls/
```

## Troubleshooting

- If the server fails to start, check logs created under `logs/` and ensure the Prisma `data.db` file exists (or update `DATABASE_URL`).
- If endpoints return validation errors, verify the payload matches the `Payroll` schema: `employee`, `position`, `gross_value`, `net_value` and `month_year` are required.

## Contributing

Contributions are welcome. Suggested flow:

1. Fork the repository
2. Create a feature branch
3. Add tests for new behavior
4. Open a Pull Request describing the change

## License

Internal use.

---

If you'd like, I can also update `modules/payroll-extract/README.md` with focused examples for running the standalone extraction scripts and exporters.
