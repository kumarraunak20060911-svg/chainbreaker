# Deployment

The supported first deployment is one application process, one bounded in-process
worker pool, and PostgreSQL on one machine. `docker-compose.yml` adds database
health checks, persistent PostgreSQL/upload/report volumes, and applies Alembic
before starting Uvicorn.

The Compose example binds the application to localhost. Put it behind an
organization-approved TLS reverse proxy before exposing it to users. Do not
publish the PostgreSQL port. Supply `CHAINBREAKER_POSTGRES_PASSWORD` and
`CHAINBREAKER_API_TOKEN` from a secret manager or shell environment; no secrets
belong in Git or `.env` files.

Production mode rejects API requests without the bearer token and tenant/user
headers. It is intentionally not advertised as a replacement for an enterprise
OIDC/SAML provider; integrate the organization's identity gateway before wider
deployment.
