# TableTap Backend Testing Guide

This document provides comprehensive information about testing the TableTap Backend application.

## Overview

The TableTap Backend uses pytest for testing with comprehensive coverage of all API endpoints and functionality. Tests are organized by application and cover both unit and integration testing scenarios.

## Test Structure

```
TableTap-v2.0-Backend/
├── apps/
│   ├── accounts/
|   |   ├── tests.py                    # Initial test file
├── pytest.ini                          # Pytest configuration
├── run_tests.py                        # Test runner script
└── TESTING.md                          # This file
```

## Running Tests

### Using the Test Runner Script

The `run_tests.py` script provides convenient ways to run different types of tests:

```bash
# Run all tests
python run_tests.py --all

# Run accounts tests only
python run_tests.py --accounts

# Run tests with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py --test apps/accounts/tests.py

# Run tests with specific marker
python run_tests.py --marker accounts

# Run linting on test files
python run_tests.py --lint
```

### Using pytest Directly

```bash
# Run all tests
pytest apps/

# Run specific app tests
pytest apps/accounts

# Run specific test file
pytest apps/accounts/tests.py

# Run tests with coverage
pytest apps/ --cov=apps.accounts --cov-report=html

# Run tests with specific markers
pytest apps/ -m accounts
pytest apps/ -m api

# Run tests with verbose output
pytest apps/ -v

# Run tests and stop on first failure
pytest apps/ -x
```

## Test Features

### Comprehensive Coverage

Each test file includes:

1. **Success Cases**: Testing normal operation with valid data
2. **Validation Tests**: Testing input validation and error handling
3. **Authentication Tests**: Testing authentication requirements
4. **Authorization Tests**: Testing permission requirements
5. **Boundary Tests**: Testing edge cases and boundary values
6. **Special Character Tests**: Testing Unicode and special character handling
7. **Data Integrity Tests**: Testing data preservation and consistency
8. **Error Handling Tests**: Testing proper error responses

### Test Data Management

- **Fixtures**: Reusable test data and objects
- **Factories**: Dynamic test data generation
- **Boundary Values**: Edge case testing data
- **Special Characters**: Unicode and special character test data

### Test Utilities

- **TestHelper**: Custom assertion methods and utilities
- **TestAssertions**: Custom assertion classes
- **TestDataFactory**: Dynamic test data creation
- **Fixtures**: Reusable test objects and data

## Test Configuration

### pytest.ini

The pytest configuration includes:

- Django settings module
- Coverage configuration
- Test discovery patterns
- Custom markers
- Output formatting

### Coverage Requirements

- Minimum coverage: 80%
- Branches: Included in coverage
- Reports: Terminal and HTML
- Apps covered: `apps.accounts`

## Test Markers

Custom markers are available for organizing tests:

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow running tests
- `accounts`: Account related tests
- `api`: API endpoint tests
- `database`: Database related tests
- `mongo`: MongoDB related tests
- `sqlite`: SQLite related tests

## Best Practices

### Writing Tests

1. **Descriptive Names**: Use clear, descriptive test method names
2. **Single Responsibility**: Each test should test one specific behavior
3. **Arrange-Act-Assert**: Structure tests with clear sections
4. **Test Data**: Use fixtures and factories for consistent test data
5. **Assertions**: Use specific assertions with clear error messages

### Test Organization

1. **Group Related Tests**: Organize tests by functionality
2. **Use Fixtures**: Reuse common test setup
3. **Parameterized Tests**: Use pytest.mark.parametrize for multiple test cases
4. **Cleanup**: Ensure tests clean up after themselves

### Error Testing

1. **Test All Error Cases**: Cover all possible error scenarios
2. **Validate Error Messages**: Check that error messages are appropriate
3. **Test Status Codes**: Verify correct HTTP status codes
4. **Test Error Formats**: Ensure error responses follow expected format


## Troubleshooting

### Common Issues

1. **Database Issues**: Ensure test database is properly configured
2. **Authentication**: Check that test users and tokens are properly created
3. **MongoDB**: Verify MongoDB connection and test database setup
4. **Dependencies**: Ensure all test dependencies are installed

### Debugging Tests

1. **Verbose Output**: Use `-v` flag for detailed output
2. **Stop on Failure**: Use `-x` flag to stop on first failure
3. **Specific Tests**: Run individual test files or methods
4. **Coverage Reports**: Generate HTML coverage reports for detailed analysis

## Contributing

When adding new tests:

1. Follow existing patterns and conventions
2. Add appropriate test markers
3. Update this documentation if needed
4. Ensure tests pass in CI/CD pipeline
5. Maintain or improve coverage percentage

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [pytest-django](https://pytest-django.readthedocs.io/)
