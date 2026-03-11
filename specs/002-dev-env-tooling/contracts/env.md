# Contract: Environment Variables (.env)

**Feature**: 002-dev-env-tooling  
**Date**: 2025-03-11

## Purpose

The application and Docker Compose use the same variable names. Variables are defined in `.env` at repository root; `.env.example` lists all required and optional variables with example or placeholder values. The application loads them via pydantic-settings (e.g. `Settings` in `src/infra/config.py`); Compose passes them to services via `env_file: .env`.

## Variables (aligned with 001-doc-to-text-api and docker-compose)

| Variable                  | Required | Description                          | Example value |
|---------------------------|----------|--------------------------------------|---------------|
| **MONGODB_URI**           | Yes      | MongoDB connection string            | `mongodb://mongodb:27017` |
| **MONGODB_DB**            | Yes      | Database name                        | `doctotext`   |
| **MAX_DOCUMENT_SIZE_BYTES**| No       | Max upload size in bytes (default: 10485760) | `10485760` |
| **ALLOWED_CONTENT_TYPES** | No       | Comma-separated or app-specific list | (app default) |

Variable names MUST match the application’s settings (e.g. `MONGODB_URI` for `mongodb_uri` in pydantic-settings, which reads env by default with uppercase mapping).

## Files

- **.env**: At repo root; gitignored; contains real values for local development. Created by copying `.env.example` and filling in values.
- **.env.example**: At repo root; committed; documents variable names and example values. No secrets.

## Loading behavior

- **Application**: pydantic-settings `BaseSettings` loads from the process environment. When running locally, the process environment MUST be populated from `.env` (e.g. by the shell, IDE, or `make run` that sources `.env` before starting the app). In Docker, Compose injects env from `env_file: .env`.
- **Docker Compose**: Uses `env_file: .env` so services receive the same variables. Compose also uses `.env` for variable substitution in the compose file itself when applicable.

## Validation and errors

- Missing required variables: Application SHOULD fail at startup with a clear message (pydantic-settings typically does this). Document in quickstart that required vars must be set in `.env`.
- Invalid values (e.g. non-numeric for MAX_DOCUMENT_SIZE_BYTES): Application SHOULD raise a validation error with an actionable message.
