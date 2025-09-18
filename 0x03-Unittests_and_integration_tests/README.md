# 0x03. Unittests and Integration Tests

This project focuses on implementing comprehensive unit tests and integration tests for Python backend applications. It demonstrates testing methodologies, mocking techniques, and parameterized testing using Python's unittest framework.

## Project Overview

The project implements and tests a GitHub organization client that interacts with the GitHub API to fetch organization and repository information. It covers:

- Unit testing with parameterized test cases
- Mocking external dependencies (HTTP requests)
- Integration testing for complete workflows
- Test-driven development practices

## Files Structure

```
0x03-Unittests_and_integration_tests/
├── README.md                    # This file
├── utils.py                     # Utility functions for data access and caching
├── client.py                    # GitHub organization client implementation
├── fixtures.py                  # Test fixtures and mock data
├── test_utils.py               # Unit tests for utility functions
├── test_client.py              # Unit and integration tests for GitHub client
└── .github/
    └── copilot-instructions.md  # Development guidelines and requirements
```

## Core Components

### 1. `utils.py`
Contains utility functions:
- **`access_nested_map(nested_map, path)`**: Safely access nested dictionary values
- **`get_json(url)`**: Fetch JSON data from HTTP endpoints
- **`memoize`**: Decorator for caching function results

### 2. `client.py`
Implements `GithubOrgClient` class:
- Fetches GitHub organization information
- Retrieves public repositories
- Filters repositories by license
- Uses memoization for performance optimization

### 3. Test Files
- **`test_utils.py`**: Parameterized tests for utility functions
- **`test_client.py`**: Comprehensive tests for GitHub client functionality

## Testing Approach

### Unit Tests
- Test individual functions in isolation
- Use mocking to eliminate external dependencies
- Parameterized testing for multiple input scenarios
- Focus on edge cases and error handling

### Integration Tests
- Test complete workflows end-to-end
- Verify component interactions
- Test with real API responses (using fixtures)

## Key Testing Concepts Demonstrated

### 1. Parameterized Testing
```python
@parameterized.expand([
    ({"a": 1}, ("a",), 1),
    ({"a": {"b": 2}}, ("a",), {"b": 2}),
    ({"a": {"b": 2}}, ("a", "b"), 2),
])
def test_access_nested_map(self, nested_map, path, expected):
    self.assertEqual(access_nested_map(nested_map, path), expected)
```

### 2. Mocking External Dependencies
```python
@patch('utils.get_json')
def test_org(self, mock_get_json):
    # Test without making actual HTTP requests
    pass
```

### 3. Property Testing
```python
@patch.object(GithubOrgClient, 'org')
def test_public_repos_url(self, mock_org):
    # Test computed properties
    pass
```

## Requirements

- **Python Version**: 3.7+ (Ubuntu 18.04 LTS compatibility)
- **Code Style**: pycodestyle (version 2.5)
- **Documentation**: All modules, classes, and functions must have docstrings
- **Type Annotations**: All functions must be type-annotated
- **File Headers**: All files must start with `#!/usr/bin/env python3`

## Dependencies

```bash
pip install parameterized
pip install requests
```

## Running Tests

### Run All Tests
```bash
python -m unittest discover
```

### Run Specific Test File
```bash
python -m unittest test_utils.py
python -m unittest test_client.py
```

### Run Specific Test Class
```bash
python -m unittest test_utils.TestAccessNestedMap
```

### Run with Verbose Output
```bash
python -m unittest -v
```

## Test Coverage

The test suite covers:
- ✅ Utility function validation
- ✅ API client functionality
- ✅ Error handling and edge cases
- ✅ Memoization behavior
- ✅ Integration workflows

## Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use type hints for all function parameters and return values
- Write comprehensive docstrings
- Keep functions focused and testable

### Testing Best Practices
- Write tests before implementation (TDD)
- Use descriptive test method names
- Test both positive and negative scenarios
- Mock external dependencies
- Keep test methods focused on single behaviors

### Documentation Standards
```python
def function_name(param: Type) -> ReturnType:
    """Brief description of function purpose.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
```

## Examples

### Testing Nested Data Access
```python
# Test accessing nested dictionary values
nested_data = {"user": {"profile": {"name": "John"}}}
result = access_nested_map(nested_data, ("user", "profile", "name"))
assert result == "John"
```

### Mocking HTTP Requests
```python
@patch('utils.get_json')
def test_api_call(self, mock_get_json):
    mock_get_json.return_value = {"status": "success"}
    client = GithubOrgClient("test-org")
    result = client.org
    mock_get_json.assert_called_once()
```

## Learning Objectives

By completing this project, you will understand:
- How to write effective unit tests
- When and how to use mocking
- Parameterized testing techniques
- Integration testing strategies
- Test-driven development workflow
- Python testing best practices

## Project Tasks

1. **Parameterize a unit test** - Test `access_nested_map` with multiple inputs
2. **Mock HTTP calls** - Test without external dependencies
3. **Parameterize and patch** - Advanced mocking techniques
4. **Patch as decorator** - Test class methods with decorators
5. **Mock property** - Test computed properties
6. **Integration tests** - End-to-end testing with fixtures

## Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [Parameterized testing](https://pypi.org/project/parameterized/)
- [Mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [GitHub API documentation](https://docs.github.com/en/rest)

---

**Note**: This project is part of the ALX Backend Python curriculum focusing on testing methodologies and best practices in Python development.