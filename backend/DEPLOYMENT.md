# FinPilot AI Deployment Guide

## Prerequisites

Before deploying the FinPilot AI backend, ensure the following are configured correctly:

### Mandatory Environment Variables

The backend application will **fail to start** if the following environment variables are missing or insecure:

- `SECRET_KEY`: **MANDATORY**. Must be exactly or longer than 32 characters in length (sufficient entropy). Weak keys and defaults will actively be rejected by the application startup routines. DO NOT use the default template key. Generate one securely using: `openssl rand -hex 32`.
- `DATABASE_URL`: Connection string for PostgreSQL.
- `REDIS_URL`: Connection string for Redis cache.
- `ENVIRONMENT`: Set to `production` or `staging`.

*Never commit `.env` files to source control.*

## Deployment Steps

1. Clone the repository onto the host server.
2. Ensure you have populated `.env` using `.env.example` as a template, paying special attention to the `SECRET_KEY`.
3. Run `docker-compose up -d --build` to launch the database, redis, and application stack.
4. Verify application health by checking the `/api/v1/system/health` endpoint.
