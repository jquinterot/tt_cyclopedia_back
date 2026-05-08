# API Robustness & Security Agent Practices

## Scope
Input validation, sanitization, rate limiting, error handling, API design consistency.

## Practices

### Input Validation
- ALL user inputs must be validated at the API boundary.
- Use Pydantic `Field(..., min_length=..., max_length=..., pattern=...)` constraints.
- Reject unexpected fields: `model_config = ConfigDict(extra='forbid')`.
- Sanitize filenames, IDs, and any string that reaches the filesystem or database.

### Rate Limiting
- Apply stricter limits to auth endpoints: 5 requests/minute for login/signup.
- Apply moderate limits to mutations: 30 requests/minute for POST/PUT/DELETE.
- Apply generous limits to reads: 100 requests/minute for GET.
- Return `429 Too Many Requests` with `Retry-After` header.

### Error Handling
- Never expose internal stack traces or exception messages in production.
- Use consistent error format: `{ "detail": "User-friendly message", "code": "ERROR_CODE" }`.
- Log full errors server-side for debugging.
- Re-raise `HTTPException` before generic `Exception` handlers.

### Authentication & Authorization
- Verify JWT on every protected endpoint.
- Check resource ownership before allowing updates/deletes.
- Admin endpoints require `is_admin=True` claim.
- Use short-lived access tokens (15 min) with refresh tokens.

### Output Safety
- Strip or escape HTML in user-generated content before rendering.
- Use parameterized queries (SQLAlchemy ORM already does this).
- Validate file uploads: whitelist MIME types, limit file size.

## Verification Checklist
- [ ] All endpoints validate input with Pydantic
- [ ] Rate limits are configured per endpoint category
- [ ] Error responses never leak internal details
- [ ] Auth checks on all protected routes
- [ ] File uploads have size and type restrictions
