# Python FastAPI Journal API

The Journal API is a FastAPI-based REST service that enables users to maintain personal journal entries. Built with Python 3.11+ and PostgreSQL, it features a robust authentication system with JWT tokens, email verification, and password reset functionality. The API follows modern security practices and includes comprehensive test coverage. Both the authentication system and journal entry management features are fully implemented and functional. The project uses SQLAlchemy for database operations, Pydantic for data validation, and includes a full test suite with pytest.

Key features:

- Secure user authentication with JWT tokens
- Email verification and password reset
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive test coverage
- API documentation via Swagger UI and ReDoc
- Modern development workflow with formatting and linting tools

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

4. Run the automated database setup script:

```bash
./scripts/setup_db.sh
```

This script will:

- Create the main database (journal_db)
- Create the test database (journal_api_test)
- Set up necessary extensions
- Apply all database migrations

Alternatively, you can set up the databases manually:

5. Create the database:

```bash
createdb journal_db
```

6. Create test database (for running tests):

```bash
createdb journal_api_test
```

7. Apply database migrations:

```bash
alembic upgrade head
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
│   │       ├── auth_endpoint.py      # Authentication endpoints
│   │       └── journal_entry_endpoint.py  # Journal entry endpoints
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
│   │   ├── auth_schema.py # Authentication schemas
│   │   └── journal_entry_schema.py # Journal entry schemas
│   ├── services/          # Business logic layer
│   │   ├── auth_service.py  # Authentication service
│   │   ├── email_service.py # Email service
│   │   └── journal_entry_service.py # Journal entry service
│   └── main.py           # FastAPI application creation
├── tests/                 # Test suite
│   ├── conftest.py       # Test configuration and fixtures
│   ├── test_auth.py      # Authentication tests
│   ├── test_models.py    # Model tests
│   └── test_journal_entries.py # Journal entry tests
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
└── Makefile             # Development commands
```

## Technical Stack

- **Core Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy, Alembic (migrations)
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
6. Create database migration if needed (`alembic revision --autogenerate -m "description"`)
7. Apply migrations (`alembic upgrade head`)
8. Commit changes
9. Create pull request

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
   - Rate limiting with configurable limits per endpoint type
   - Security headers and CORS configuration

2. **Journal Entry API**
   - Complete CRUD operations for journal entries
   - User-specific entry filtering and access control
   - Entry validation and error handling
   - UUID-based entry identification
   - Timestamp tracking (created_at, updated_at)
   - Bulk delete functionality

3. **Database Infrastructure**
   - Automated database setup script
   - Database migrations with Alembic
   - User model with UUID, email, and password
   - Journal entry model with work, struggle, and intention fields
   - Proper relationship setup between models

4. **Testing Infrastructure**
   - Test database configuration
   - Database transaction fixtures
   - Email service mocking
   - Authentication test suite

## 🎉 Project Status: Complete

This Journal API is **fully functional** with all core features implemented:

- ✅ **Complete Authentication System** - Registration, login, token refresh, password reset
- ✅ **Complete Journal Entry CRUD** - Create, read, update, delete operations
- ✅ **User Authorization** - Secure access to user-specific journal entries
- ✅ **Database Integration** - PostgreSQL with SQLAlchemy ORM
- ✅ **Comprehensive Testing** - Full test suite with pytest
- ✅ **API Documentation** - Auto-generated OpenAPI/Swagger docs
- ✅ **Rate Limiting** - Protection against abuse
- ✅ **Email Integration** - Password reset functionality

The API is production-ready and can be deployed immediately.

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

| Method | Endpoint        | Description                               | Status     |
| ------ | --------------- | ----------------------------------------- | ---------- |
| POST   | `/entries`      | Create a new journal entry                | ✅ Complete |
| GET    | `/entries`      | List all entries for authenticated user   | ✅ Complete |
| GET    | `/entries/{id}` | Get a specific entry by ID                | ✅ Complete |
| PUT    | `/entries/{id}` | Update an existing entry                  | ✅ Complete |
| DELETE | `/entries/{id}` | Delete a specific entry                   | ✅ Complete |
| DELETE | `/entries`      | Delete all entries for authenticated user | ✅ Complete |

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

## Journal Entry API Examples

```bash
# Create a new journal entry (requires authentication)
curl -X POST http://localhost:8000/api/v1/entries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "work": "Completed the authentication system for the journal API",
    "struggle": "Had some issues with JWT token validation initially",
    "intention": "Tomorrow I will work on improving the error handling"
  }'
```

```bash
# Get all journal entries for the authenticated user
curl -X GET http://localhost:8000/api/v1/entries \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Get a specific journal entry by ID
curl -X GET http://localhost:8000/api/v1/entries/ENTRY_UUID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Update a journal entry
curl -X PUT http://localhost:8000/api/v1/entries/ENTRY_UUID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "work": "Updated the journal entry endpoints",
    "struggle": "Debugging some async database issues",
    "intention": "Focus on adding comprehensive tests tomorrow"
  }'
```

```bash
# Delete a specific journal entry
curl -X DELETE http://localhost:8000/api/v1/entries/ENTRY_UUID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Delete all journal entries for the authenticated user
curl -X DELETE http://localhost:8000/api/v1/entries \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Note: Replace `YOUR_ACCESS_TOKEN` with the actual JWT access token received from the login endpoint, and `ENTRY_UUID` with the actual UUID of a journal entry.

## Database Migrations

The project uses Alembic for database migrations. Here are common migration commands:

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current migration status
alembic current
```

All migrations are stored in the `migrations/versions/` directory and are version controlled. This ensures consistent database schema across all environments.

The initial migration includes:

- User table with UUID, email, and password fields
- Journal entry table with work, struggle, and intention fields
- Proper indexes and foreign key relationships
- Timestamp fields for auditing
