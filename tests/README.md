# MacroCalc Testing Suite

This directory contains unit tests for the MacroCalc application.

## Test Structure

- `conftest.py`: Test fixtures and configuration
- `test_models.py`: Tests for database models (User, MacroPost, FeedPost, SharedPost, FriendRequest)
- `test_routes.py`: Tests for application routes
- `test_forms.py`: Tests for form validation
- `test_friend_requests.py`: Tests for friend request functionality
- `test_shared_posts.py`: Tests for shared posts functionality

## Running Tests

To run the full test suite:

```bash
python -m pytest
```

To run a specific test file:

```bash
python -m pytest tests/test_models.py
```

To run a specific test function:

```bash
python -m pytest tests/test_models.py::test_user_model
```

To run tests with verbose output:

```bash
python -m pytest -v
```

## Test Coverage

You can generate test coverage reports by installing pytest-cov:

```bash
pip install pytest-cov
```

Then run:

```bash
python -m pytest --cov=app tests/
```

For a detailed HTML coverage report:

```bash
python -m pytest --cov=app --cov-report=html tests/
```

This will create a directory called `htmlcov` with an HTML coverage report.

## Important Notes

1. The tests use an in-memory SQLite database, so they don't affect the development database.
2. Tests will generate unique usernames and emails to avoid unique constraint violations.
3. If you add new models or change existing ones, make sure to update the tests accordingly. 