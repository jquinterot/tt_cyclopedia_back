# Backend Domain Agent Practices

## Scope
Python/FastAPI backend: test coverage, Pydantic validation, query optimization, error handling, code quality.

## Practices

### Testing
- ALWAYS run `docker-compose run --rm test` before any push. Local `pytest` is NOT enough.
- When adding new models: import to `app/migrations/env.py`, generate migration, run Docker tests.
- Target: >80% coverage for all routers. Use pytest-cov to measure.
- Test both success and error paths. Mock external services (Cloudinary, MongoDB).
- Use `TestClient` from FastAPI for integration tests.

### Code Quality
- Use Pydantic v2 models for all request/response schemas in `schemas.py`.
- Add explicit `Field(..., max_length=..., description=...)` validation.
- Use SQLAlchemy 2.0 style (`select()`, `session.execute()`).
- Avoid N+1 queries: use `selectinload()` for relationships.
- Standardize error responses: always return JSON with `{ "detail": "..." }`.
- Never leak internal exception messages in production responses.
- Use type hints everywhere. Run `mypy` if available.

### Security
- Input sanitization on all user-provided fields.
- Rate limiting on mutation endpoints (POST/PUT/DELETE).
- Admin checks for destructive operations.
- Never commit secrets. Rotate exposed credentials immediately.

### Performance
- Add pagination to all list endpoints (`skip`/`limit` or cursor-based).
- Use database indexes for frequently queried columns.
- Profile slow queries with `EXPLAIN ANALYZE`.

## Verification Checklist
- [ ] Docker tests pass: `docker-compose run --rm test`
- [ ] New tests added for changed code
- [ ] No N+1 queries introduced
- [ ] All endpoints have Pydantic request/response models
- [ ] Error messages are user-friendly, not internal tracebacks
