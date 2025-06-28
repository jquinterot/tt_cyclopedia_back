# Unit Tests for FastAPI Backend

This directory contains comprehensive unit tests for all endpoints in the FastAPI application.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and fixtures
- **`test_users.py`** - Tests for user management endpoints
- **`test_posts.py`** - Tests for post management endpoints  
- **`test_comments.py`** - Tests for comment management endpoints
- **`test_forums.py`** - Tests for forum management endpoints
- **`run_tests.py`** - Test runner script

### Test Coverage

Each test file covers the following scenarios:

#### Users Router (`test_users.py`)
- ✅ User registration
- ✅ User login/logout
- ✅ User retrieval (all users, by ID)
- ✅ Password hashing verification
- ✅ Duplicate username/email handling
- ✅ Invalid data validation
- ✅ Authentication requirements

#### Posts Router (`test_posts.py`)
- ✅ Post creation with/without images
- ✅ Post retrieval (all posts, by ID)
- ✅ Post deletion (owner only)
- ✅ Post likes/unlikes
- ✅ Like count tracking
- ✅ File upload validation
- ✅ Stats JSON handling
- ✅ Authorization checks

#### Comments Router (`test_comments.py`)
- ✅ Comment creation (posts and forums)
- ✅ Comment replies and threading
- ✅ Comment updates (owner only)
- ✅ Comment deletion with replies
- ✅ Comment likes/unlikes
- ✅ Comment retrieval by post/forum
- ✅ Main comments vs replies filtering
- ✅ Authorization and ownership checks

#### Forums Router (`test_forums.py`)
- ✅ Forum creation and management
- ✅ Forum retrieval (all forums, by ID)
- ✅ Forum updates (owner only)
- ✅ Forum deletion (owner only)
- ✅ Forum likes/unlikes
- ✅ Forum comments management
- ✅ Forum comment replies
- ✅ Authorization and ownership checks

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-cov pytest-asyncio
```

### Run All Tests

```bash
# Using pytest directly
pytest app/tests/ -v

# Using the test runner script
python app/tests/run_tests.py

# Using pytest with coverage
pytest app/tests/ --cov=app --cov-report=html
```

### Run Specific Test Files

```bash
# Run only user tests
pytest app/tests/test_users.py -v

# Run only post tests
pytest app/tests/test_posts.py -v

# Run only comment tests
pytest app/tests/test_comments.py -v

# Run only forum tests
pytest app/tests/test_forums.py -v

# Using the test runner script
python app/tests/run_tests.py test_users.py
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### Database Setup
Tests use an in-memory SQLite database for isolation and speed:
- Each test gets a fresh database session
- Tables are created and dropped for each test
- No data persists between tests

### Authentication
Tests include authentication fixtures:
- `test_user` - Primary test user
- `test_user2` - Secondary test user for ownership tests
- `auth_headers` - Authentication headers for primary user
- `auth_headers_user2` - Authentication headers for secondary user

### Test Data Fixtures
- `test_post` - Sample post for testing
- `test_forum` - Sample forum for testing
- `test_comment` - Sample comment for testing
- `test_forum_comment` - Sample forum comment for testing

## Test Patterns

### Success Cases
Each endpoint has tests for successful operations:
- Proper status codes (200, 201, 204)
- Correct response data structure
- Expected field values

### Error Cases
Comprehensive error handling tests:
- 401 Unauthorized (missing authentication)
- 403 Forbidden (wrong ownership)
- 404 Not Found (invalid IDs)
- 422 Unprocessable Entity (invalid data)
- 400 Bad Request (business logic errors)

### Authorization Tests
Tests verify proper access control:
- Unauthenticated requests are rejected
- Users can only modify their own content
- Admin operations require proper permissions

### Data Validation
Tests ensure data integrity:
- Required fields are validated
- Data types are enforced
- Business rules are applied

## Coverage Reports

After running tests, coverage reports are generated:
- **Terminal output** - Shows missing lines
- **HTML report** - Detailed coverage in `htmlcov/` directory
- **XML report** - For CI/CD integration

## Best Practices

### Test Isolation
- Each test is independent
- Database is reset between tests
- No shared state between tests

### Descriptive Names
- Test names clearly describe what they test
- Include expected outcome in name
- Use consistent naming patterns

### Comprehensive Coverage
- Test both success and failure paths
- Include edge cases and boundary conditions
- Test all HTTP methods and status codes

### Fast Execution
- Use in-memory database
- Minimize external dependencies
- Avoid slow operations in tests

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- No external dependencies
- Consistent results across environments
- Clear pass/fail indicators
- Coverage reporting for quality gates

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure app directory is in Python path
2. **Database Errors**: Check that SQLite is available
3. **Authentication Errors**: Verify JWT configuration
4. **Missing Dependencies**: Install pytest and related packages

### Debug Mode

Run tests with more verbose output:
```bash
pytest -v -s --tb=long
```

### Test Development

When adding new tests:
1. Follow existing naming conventions
2. Use appropriate fixtures
3. Test both success and error cases
4. Update this README if adding new test categories 