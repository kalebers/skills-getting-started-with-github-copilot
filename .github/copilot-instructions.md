# Copilot instructions for this repository

## Project overview

This repository is a small FastAPI application for Mergington High School extracurricular activities. The app exposes a simple REST API and serves a browser UI from the static assets directory. Most of the behavior is concentrated in a few routes and a single in-memory data store, so understanding the interaction between the API and the static frontend is the key to making safe changes.

- Application entry point: `src/app.py`
- Static frontend: `src/static/`
- Project docs: `src/README.md`
- Root `README.md` is mostly a course scaffold; prefer `src/README.md` for app-specific behavior

## Build, run, and test commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app locally:

```bash
cd src && python app.py
```

Or from the repo root:

```bash
python -m uvicorn src.app:app --reload
```

Open the local app at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

Test commands:

```bash
pytest -q
```

Run a single test file:

```bash
pytest tests/test_app.py -q
```

Run a specific test:

```bash
pytest tests/test_app.py::test_signup_for_activity -q
```

There is no dedicated lint configuration in this repo. The project currently relies on `pytest` validation and the FastAPI app startup path rather than a repo-specific lint command.

## High-level architecture

The app intentionally keeps the implementation very small and follows a single-file backend pattern:

- `src/app.py` creates the `FastAPI` app, mounts `/static`, and defines the in-memory activities registry.
- `activities` is a Python dictionary keyed by activity name, each value containing:
  - `description`
  - `schedule`
  - `max_participants`
  - `participants`
- The root route (`/`) redirects to `/static/index.html`, where the browser UI loads and calls the API endpoints.
- The frontend does not use a database or backend framework beyond the FastAPI app; all data resets when the process restarts.

The important API surface is:

- `GET /activities` — fetch the full activity catalog
- `POST /activities/{activity_name}/signup` — register a student for an activity
- `DELETE /activities/{activity_name}/signup` — remove a signup

## Key codebase conventions

- Treat activity names as canonical identifiers. They are used as dictionary keys and also in URL paths, so editing the name of an activity is not a cosmetic change.
- Maintain the existing in-memory shape of each activity object. New fields should be added only if the frontend and tests are updated consistently.
- Validate duplicate signups and unknown activities explicitly with `HTTPException` status codes:
  - `404` when an activity does not exist
  - `400` when a student is already signed up
- Keep the `participants` list as the source of truth for signups and membership checks.
- Preserve the `Cache-Control: no-store` behavior on `GET /activities` so the UI does not cache stale activity data.
- If you add tests, use `TestClient` against `src.app:app` rather than building a separate mock API layer.
- Prefer changes that remain consistent with the exercise’s intentionally simple architecture: no database layer, no ORM, no persistent storage, no background jobs.

## Worked example of the expected pattern

A safe change in this codebase usually follows this pattern:

1. Update the in-memory `activities` data or route behavior in `src/app.py`.
2. Confirm the static frontend still calls the expected endpoint contracts.
3. Validate with the smallest relevant `pytest` invocation.
4. Confirm the app still starts via `uvicorn` or `python app.py`.

This repository is small enough that the fastest safe path is usually to inspect `src/app.py` first, then verify the static UI and endpoint contracts before making changes.
