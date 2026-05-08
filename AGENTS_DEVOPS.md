# DevOps Domain Agent Practices

## Scope
CI/CD, Docker, pre-commit hooks, linting, GitHub Actions, tooling automation.

## Practices

### CI/CD Pipeline
- GitHub Actions workflow must run on every PR and push to main.
- Backend CI: `docker-compose run --rm test` (the ONLY way to validate migrations).
- Frontend CI: `npm run unit:test -- --run` and `npm run build`.
- Block merges if CI fails. Require at least 1 review.

### Pre-commit Hooks
- Use `pre-commit` framework with these hooks:
  - `trailing-whitespace`
  - `end-of-file-fixer`
  - `check-yaml`
  - `check-added-large-files` (max 500KB)
  - `black` (Python formatter)
  - `ruff` (Python linter)
  - `eslint --fix` (Frontend)
  - `prettier --write` (Frontend)
- Install hooks: `pre-commit install`

### Docker
- Multi-stage builds for smaller production images.
- Use `.dockerignore` to exclude `.venv`, `node_modules`, `.git`.
- Pin base image versions (`python:3.12-slim-bookworm`, not `python:latest`).

### Secrets Management
- NEVER commit `.env` files. Use `.env.example` with dummy values.
- Rotate any secret that was ever committed, even if later removed.
- Use GitHub Secrets for CI environment variables.

### Linting
- Python: `ruff` for linting, `black` for formatting.
- TypeScript: `eslint` with `@typescript-eslint/recommended`.
- Enforce in CI: fail build on lint errors.

## Verification Checklist
- [ ] `.pre-commit-config.yaml` exists and hooks run cleanly
- [ ] GitHub Actions workflow file exists in `.github/workflows/`
- [ ] CI passes on this branch
- [ ] No secrets in committed files
- [ ] Docker build succeeds: `docker-compose build`
