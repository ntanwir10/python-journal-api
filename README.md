# Python FastAPI Journal API

Inspired by [Learn To Cloud](https://learntocloud.guide/)'s [Journal Starter](https://github.com/learntocloud/journal-starter) capstone project. Rather than forking the repository, this is a from-scratch implementation.

## Prerequisites

- Python 3.11+
- PostgreSQL 17
- Poetry (optional)

## Database Setup

1. Install PostgreSQL 17:

```bash
brew install postgresql@17
```

2. Start PostgreSQL service:

```bash
brew services start postgresql@17
```

3. Add PostgreSQL to your PATH:

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

4. Create the database:

```bash
createdb journal_db
```

5. Create test database (for running tests):

```bash
createdb journal_api_test
```

## Environment Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials and other settings:

```JSON
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=journal_db
POSTGRES_TEST_DB=journal_api_test
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=15
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

## Project Structure

```txt
journal-api/
├── app/                    # Application package
│   ├── api/               # API routes and endpoints
│   │   └── v1/           # Version 1 API endpoints
│   │       └── auth_endpoint.py  # Authentication endpoints
│   ├── core/              # Core functionality
│   │   ├── config.py      # Application settings
│   │   └── auth_middleware.py  # JWT authentication middleware
│   ├── db/                # Database related files
│   │   ├── base.py        # SQLAlchemy declarative base
│   │   └── session.py     # Database session management
│   ├── models/            # SQLAlchemy models
│   │   ├── user_model.py  # User model
│   │   └── journal_entry_model.py  # Journal entry model
│   ├── schemas/           # Pydantic models/schemas
│   │   └── auth_schema.py # Authentication schemas
│   ├── services/          # Business logic layer
│   │   ├── auth_service.py  # Authentication service
│   │   └── email_service.py # Email service
│   └── main.py           # FastAPI application creation
├── tests/                 # Test suite
│   ├── conftest.py       # Test configuration and fixtures
│   ├── test_auth.py      # Authentication tests
│   └── test_models.py    # Model tests
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
└── Makefile             # Development commands
```

## Technical Stack

- **Core Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy
- **Security**: Python-Jose (JWT), Passlib (bcrypt)
- **Validation**: Pydantic v2
- **Testing**: Pytest, httpx
- **Development Tools**: Black (formatting), Flake8 (linting), isort (import sorting)

## Development Workflow

1. Create feature branch
2. Implement feature/fix
3. Run tests (`make test`)
4. Format code (`make format`)
5. Run linting (`make lint`)
6. Commit changes
7. Create pull request

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and update the values
3. Install dependencies: `make install`
4. Start the development server: `make dev`
5. Run tests: `make test`

## Implementation Status

### ✅ Completed Features

1. **Authentication System**
   - User registration with email verification
   - Login with JWT token generation
   - Token refresh mechanism
   - Password reset flow with email
   - Secure password hashing with bcrypt
   - Comprehensive test suite
   - Rate limiting and security headers

2. **Database Models**
   - User model with UUID, email, and password
   - Journal entry model with work, struggle, and intention fields
   - Proper relationship setup between models

3. **Testing Infrastructure**
   - Test database configuration
   - Database transaction fixtures
   - Email service mocking
   - Authentication test suite

### 🚧 In Progress

1. **Journal Entry API**
   - CRUD operations for journal entries
   - User-specific entry filtering
   - Entry validation and error handling

## API Documentation

Once running, API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## API Endpoints

### Authentication Endpoints

| Method | Endpoint                | Description                              | Status     |
| ------ | ----------------------- | ---------------------------------------- | ---------- |
| POST   | `/auth/signup`          | Register a new user                      | ✅ Complete |
| POST   | `/auth/login`           | Authenticate user and get tokens         | ✅ Complete |
| POST   | `/auth/refresh`         | Get new access token using refresh token | ✅ Complete |
| POST   | `/auth/logout`          | Invalidate current tokens                | ✅ Complete |
| POST   | `/auth/forgot-password` | Request password reset email             | ✅ Complete |
| POST   | `/auth/reset-password`  | Reset password using token from email    | ✅ Complete |

### Journal Entry Endpoints

| Method | Endpoint        | Description                               | Status        |
| ------ | --------------- | ----------------------------------------- | ------------- |
| POST   | `/entries`      | Create a new journal entry                | 🚧 In Progress |
| GET    | `/entries`      | List all entries for authenticated user   | 🚧 In Progress |
| GET    | `/entries/{id}` | Get a specific entry by ID                | 🚧 In Progress |
| PUT    | `/entries/{id}` | Update an existing entry                  | 🚧 In Progress |
| DELETE | `/entries/{id}` | Delete a specific entry                   | 🚧 In Progress |
| DELETE | `/entries`      | Delete all entries for authenticated user | 🚧 In Progress |

## Authentication API Examples

```bash
# Sign-up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

```bash
# Refresh Token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

```bash
# Logout (requires auth token)
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Request Password Reset
curl -X POST http://localhost:8000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

```bash
# Reset Password (using reset token)
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "newSecurePassword123"
  }'
```

Note: Replace `YOUR_ACCESS_TOKEN` and `YOUR_REFRESH_TOKEN` with the actual JWT tokens received from the login endpoint.

## Journal Entry API Examples (Coming Soon)

The Journal Entry API endpoints are currently under development. Once completed, examples will be provided here.
