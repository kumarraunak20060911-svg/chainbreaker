# Database and job operations

PostgreSQL is the default production database. SQLAlchemy 2.x provides the
transaction and connection-pool boundary, and Alembic owns schema migrations.
SQLite is used only for isolated tests and local compatibility tooling.

The initial migration creates tenant-scoped tables for organizations, users, data
sources, ingestion jobs, security events, detection findings, investigation cases,
case/finding associations, graph nodes, graph edges, graph-edge evidence,
investigation reports, and audit events. Frequently queried organization,
timestamp, source, entity, severity, case, job, and graph score columns are
explicit indexed columns; flexible features and provenance use JSON/JSONB.

Apply migrations with:

```bash
python -m alembic upgrade head
```

Do not reset or drop the database during application startup. Use the normal
PostgreSQL backup flow, for example:

```bash
pg_dump "$CHAINBREAKER_DATABASE_URL" > chainbreaker-backup.sql
psql "$CHAINBREAKER_DATABASE_URL" < chainbreaker-backup.sql
```

The durable job state is:

```text
PENDING -> RUNNING -> SUCCEEDED
                  -> FAILED
                  -> RETRYING -> RUNNING
                  -> CANCELLED
```

Workers claim jobs with a conditional update and a lease timestamp. Event
fingerprints make retries idempotent, and malformed rows are counted rather than
silently discarded. The initial worker is in-process and bounded to two threads;
run it under a process supervisor and replace it with an external worker only when
queue-depth and latency measurements justify that change.
