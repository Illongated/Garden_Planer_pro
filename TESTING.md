# Comprehensive Testing Strategy

## Overview

This document outlines the complete testing strategy for the Agrotique Garden Planner, covering backend, frontend, security, performance, and system testing.

## Testing Pyramid

```
    E2E Tests (10%)
   ┌─────────────┐
   │             │
   │ Integration │ (20%)
   │   Tests     │
   └─────────────┘
   ┌─────────────┐
   │             │
   │   Unit      │ (70%)
   │   Tests     │
   └─────────────┘
```

## Backend Testing

### Unit Tests

**Location**: `app/tests/test_*.py`

**Coverage**: >90% code coverage

**Test Types**:
- Model validation and relationships
- CRUD operations
- Business logic calculations
- Service layer functionality
- Utility functions

**Running Tests**:
```bash
# Run all backend tests
pytest

# Run specific test file
pytest app/tests/test_models.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test markers
pytest -m unit
pytest -m integration
pytest -m security
```

### API Integration Tests

**Location**: `app/tests/test_api_integration.py`

**Coverage**: All API endpoints

**Test Types**:
- Authentication and authorization
- CRUD operations via API
- Error handling
- Response validation
- Rate limiting

**Running Tests**:
```bash
# Run API tests
pytest -m api

# Run with specific endpoint
pytest app/tests/test_api_integration.py::TestGardenEndpoints
```

### Security Tests

**Location**: `app/tests/test_security.py`

**Coverage**: Security vulnerabilities

**Test Types**:
- SQL injection prevention
- XSS protection
- Authentication bypass
- Input validation
- Path traversal
- Command injection

**Running Tests**:
```bash
# Run security tests
pytest -m security

# Run specific security test
pytest app/tests/test_security.py::TestSQLInjection
```

### Performance Tests

**Location**: `app/tests/test_performance.py`

**Coverage**: Performance metrics

**Test Types**:
- Response time testing
- Throughput testing
- Load testing
- Memory usage testing
- CPU-intensive operations

**Running Tests**:
```bash
# Run performance tests
pytest -m performance

# Run with specific performance test
pytest app/tests/test_performance.py::TestResponseTime
```

## Frontend Testing

### Unit Tests

**Location**: `src/**/*.test.tsx`

**Coverage**: >80% code coverage

**Test Types**:
- Component rendering
- User interactions
- State management
- Hook testing
- Utility functions

**Running Tests**:
```bash
# Run all frontend tests
npm run test:unit

# Run specific test file
npm run test:unit -- src/components/Button.test.tsx

# Run with coverage
npm run test:unit -- --coverage
```

### Component Tests

**Example**: `src/components/ui/__tests__/button.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Hook Tests

**Example**: `src/hooks/__tests__/use-api.test.ts`

```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { useApi } from '../use-api'

describe('useApi', () => {
  it('fetches data successfully', async () => {
    const { result } = renderHook(() => useApi('/test-endpoint'))
    
    await waitFor(() => {
      expect(result.current.data).toBeDefined()
    })
  })
})
```

### E2E Tests

**Location**: `src/tests/e2e/`

**Framework**: Playwright

**Test Types**:
- User workflows
- Cross-browser testing
- Mobile responsiveness
- Accessibility testing

**Running Tests**:
```bash
# Run E2E tests
npm run test:e2e

# Run specific browser
npm run test:e2e -- --project=chromium

# Run with UI
npm run test:e2e -- --ui
```

## Test Configuration

### Backend Configuration

**File**: `pytest.ini`

```ini
[tool:pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
```

### Frontend Configuration

**File**: `vitest.config.ts`

```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
})
```

## Test Fixtures and Utilities

### Backend Fixtures

**File**: `app/tests/conftest.py`

```python
@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    user = user_crud.create(db_session, obj_in=user_data)
    return user

@pytest.fixture
def authenticated_client(client, test_user_token):
    """Create authenticated test client."""
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client
```

### Frontend Utilities

**File**: `src/test/setup.ts`

```typescript
global.testUtils = {
  mockApiResponse: (data: any) => Promise.resolve({ data }),
  mockApiError: (error: any) => Promise.reject(error),
  createMockUser: () => ({
    id: 'test-user-id',
    email: 'test@example.com',
    full_name: 'Test User',
  }),
}
```

## CI/CD Integration

### GitHub Actions

**File**: `.github/workflows/ci.yml`

**Jobs**:
1. **Backend Tests**: Unit, integration, security, performance
2. **Frontend Tests**: Unit, component, E2E
3. **Security Tests**: Static analysis, vulnerability scanning
4. **Performance Tests**: Load testing, response time
5. **Build**: Docker image creation
6. **Quality Gate**: Coverage and quality checks
7. **Deploy**: Staging and production deployment

### Quality Gates

**Requirements**:
- Backend coverage > 90%
- Frontend coverage > 80%
- No critical security vulnerabilities
- Performance benchmarks met
- All tests passing

## Testing Best Practices

### Backend Testing

1. **Use Fixtures**: Reuse test data and setup
2. **Mock External Dependencies**: Database, APIs, services
3. **Test Edge Cases**: Invalid input, error conditions
4. **Use Descriptive Names**: Clear test function names
5. **Group Related Tests**: Use test classes and markers

### Frontend Testing

1. **Test User Behavior**: Focus on user interactions
2. **Mock API Calls**: Use MSW or similar
3. **Test Accessibility**: Include a11y testing
4. **Use Testing Library**: Follow testing library best practices
5. **Test Responsive Design**: Mobile and desktop layouts

### Security Testing

1. **Input Validation**: Test all user inputs
2. **Authentication**: Test all auth flows
3. **Authorization**: Test access controls
4. **Data Sanitization**: Test XSS prevention
5. **SQL Injection**: Test database queries

### Performance Testing

1. **Response Times**: Measure API response times
2. **Throughput**: Test concurrent requests
3. **Memory Usage**: Monitor memory consumption
4. **Load Testing**: Test under high load
5. **Scalability**: Test with increasing load

## Test Data Management

### Backend Test Data

```python
# Factory pattern for test data
class TestDataFactory:
    @staticmethod
    def create_user(**kwargs):
        return User(
            email=kwargs.get('email', 'test@example.com'),
            full_name=kwargs.get('full_name', 'Test User'),
            **kwargs
        )
    
    @staticmethod
    def create_garden(**kwargs):
        return Garden(
            name=kwargs.get('name', 'Test Garden'),
            width=kwargs.get('width', 10.0),
            height=kwargs.get('height', 8.0),
            **kwargs
        )
```

### Frontend Test Data

```typescript
// Mock data factories
export const createMockUser = (overrides = {}) => ({
  id: 'test-user-id',
  email: 'test@example.com',
  full_name: 'Test User',
  ...overrides,
})

export const createMockGarden = (overrides = {}) => ({
  id: 'test-garden-id',
  name: 'Test Garden',
  description: 'A test garden',
  width: 10.0,
  height: 8.0,
  ...overrides,
})
```

## Coverage Reports

### Backend Coverage

**Command**: `pytest --cov=app --cov-report=html`

**Reports**:
- HTML: `htmlcov/index.html`
- XML: `coverage.xml`
- Terminal: Missing lines display

### Frontend Coverage

**Command**: `npm run test:unit -- --coverage`

**Reports**:
- HTML: `coverage/lcov-report/index.html`
- JSON: `coverage/coverage-final.json`
- Terminal: Coverage summary

## Debugging Tests

### Backend Debugging

```bash
# Run with debugger
pytest --pdb

# Run specific test with debugger
pytest -x --pdb app/tests/test_models.py::TestUserModel::test_create_user

# Run with verbose output
pytest -v -s
```

### Frontend Debugging

```bash
# Run tests in watch mode
npm run test:unit -- --watch

# Run with debugger
npm run test:unit -- --inspect-brk

# Run specific test file
npm run test:unit -- src/components/Button.test.tsx
```

## Performance Testing

### Load Testing

**Tool**: Locust

**File**: `performance_tests/locustfile.py`

```python
from locust import HttpUser, task, between

class GardenPlannerUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_gardens(self):
        self.client.get("/api/v1/gardens/")
    
    @task
    def create_garden(self):
        self.client.post("/api/v1/gardens/", json={
            "name": "Test Garden",
            "width": 10.0,
            "height": 8.0
        })
```

### Running Performance Tests

```bash
# Run load test
locust -f performance_tests/locustfile.py

# Run headless
locust -f performance_tests/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 60s
```

## Accessibility Testing

### Tools

1. **axe-core**: Automated accessibility testing
2. **Playwright**: Manual accessibility testing
3. **Screen Readers**: NVDA, JAWS testing

### Implementation

```typescript
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

test('should not have accessibility violations', async () => {
  const { container } = render(<MyComponent />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

## Visual Regression Testing

### Tools

1. **Playwright**: Screenshot comparison
2. **Percy**: Visual testing platform
3. **Chromatic**: Storybook visual testing

### Implementation

```typescript
test('visual regression', async ({ page }) => {
  await page.goto('/garden-planner')
  await expect(page).toHaveScreenshot('garden-planner-page.png')
})
```

## Continuous Monitoring

### Test Metrics

1. **Coverage Trends**: Track coverage over time
2. **Test Duration**: Monitor test execution time
3. **Flaky Tests**: Identify and fix unstable tests
4. **Performance Trends**: Track performance metrics

### Reporting

1. **Coverage Reports**: HTML and XML reports
2. **Test Results**: JUnit XML format
3. **Performance Reports**: Locust HTML reports
4. **Security Reports**: Bandit and Safety reports

## Conclusion

This comprehensive testing strategy ensures:

- **Quality**: High code coverage and thorough testing
- **Security**: Vulnerability prevention and detection
- **Performance**: Load testing and optimization
- **Reliability**: Automated testing and CI/CD integration
- **Maintainability**: Clear test organization and documentation

The testing pyramid approach ensures that most tests are fast, reliable unit tests, with fewer integration and E2E tests that are slower but provide broader coverage. 