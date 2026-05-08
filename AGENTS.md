# Agent Workflow: Pre-Push Checklist

## CRITICAL RULE: Never Push Before Running Local Tests

Before every `git push`, you MUST run the full Docker test suite locally.
The local pytest (`pytest app/tests/`) is NOT enough because it reuses your existing database.
CI spins up a fresh database and runs Alembic migrations — your local DB likely already has tables from manual seeding.

## Backend Pre-Push Steps

```bash
# 1. Run the exact same test command CI uses
docker-compose run --rm test

# This does:
# - Spin up fresh PostgreSQL + MongoDB containers
# - Build test image
# - Run `alembic upgrade head` on fresh DB
# - Run `pytest app/tests/ -v --tb=short --maxfail=1`
```

## Common CI-Only Failures

| Issue | Why Local Passes | Why CI Fails |
|-------|-----------------|--------------|
| Missing migration | Local DB seeded with `Base.metadata.create_all()` | CI only runs Alembic migrations |
| Missing column | Local DB has column from manual `ALTER TABLE` | Fresh DB only has columns in migrations |
| Wrong migration order | Local alembic_version table out of sync | CI runs migrations sequentially on clean DB |

## When You Add New Models

1. Add model import to `app/migrations/env.py`
2. Generate migration: `python3 -m alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Run Docker tests: `docker-compose run --rm test`
5. Only then push

## When CI Fails After Push

1. Read CI logs carefully
2. Reproduce locally with: `docker-compose run --rm test`
3. Fix the issue
4. Run Docker tests again to confirm
5. Then push

## Frontend Pre-Push Steps

```bash
npm run unit:test -- --run
```

## Remember

> "Tests green on my machine" is NOT good enough.
> "Tests green in Docker on my machine" is the minimum.
