# CITS3403-project

1. Project description, Explain design and use

Our application is a Macro calculator which allows users to input their details: height, age, weight, gender, activity level and calorie goal. 

They can then view a calculated recommended daily calorie intake which they can share with others to compare results. 

If a user set their calorie goal as a "Deficit" overtime if they ate the recommended calories they will lose weight. As the user's weight changes they can recalculate new results to view comparisons graphed overtime.

Our Project 

2. |      Name     |   Student ID  | Github username |
   | ------------  | ------------- | ------------- |
   | Noah Gibson  | 23339303  | noahgibson710  | 
   | Tahjeeb Tajwar  | 23738292  |  tajwar0011 |
   | Yimian Wang   | 23845246  | wangyimian812  | 
   | Arun Arjunan  | 23971914   | aruncancode |

3. Instructions for how to launch the application

The application can be launched by:

First installing the required packages (requirements.txt)

do this by creating a venv using: python -m venv venv

then activate it using: venv\Scripts\activate for windows(command prompt) or source venv/bin/activate for mac or linux

now use: pip install -r requirements.txt

then run python app.py which runs the flask application

finally control+click the localhost url that appears in the terminal it will open in your default browser and take you to the home page

4. Instructions for how to run tests


## Test Structure

- `conftest.py`: Test fixtures and configuration
- `test_models.py`: Tests for database models (User, MacroPost, FeedPost, SharedPost, FriendRequest)
- `test_routes.py`: Tests for application routes
- `test_forms.py`: Tests for form validation
- `test_friend_requests.py`: Tests for friend request functionality
- `test_shared_posts.py`: Tests for shared posts functionality
- `core_tests.py`: End-to-end tests for user registration, login, macro calculation, profile updates, friend requests, and post sharing
- `test_selenium_app.py`: Selenium-based browser tests for signup, login, and calculator UI flows

## Running Tests

To run the full test suite:

```bash
python -m pytest
```

To run a specific test file (e.g., core_tests.py or test_selenium_app.py):

```bash
python -m pytest tests/core_tests.py
python -m pytest tests/test_selenium_app.py
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
