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

Then edit `.env` with your database credentials:

```JSON
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=journal_db
SECRET_KEY=your_secret_key
```

## Project Structure

```txt
journal-api/
├── app/                    # Application package
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core functionality
│   │   └── config.py      # Application settings and configurations
│   ├── db/                # Database related files
│   │   ├── base.py        # SQLAlchemy declarative base
│   │   └── session.py     # Database session management
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic models/schemas for request/response
│   ├── services/          # Business logic layer
│   └── main.py           # FastAPI application creation and configuration
├── .env.example           # Example environment variables
├── requirements.txt       # Project dependencies
└── Makefile              # Development commands
```

## Technical Stack

- **Core Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy
- **Security**: Python-Jose (JWT), Passlib (bcrypt)
- **Validation**: Pydantic v2
- **Testing**: Pytest
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

## Implementation Tasks

### 1. Core API Development

- [ ] POST /entries - Creates an entry
- [ ] GET /entries - List all entries
- [ ] GET /entries/{id} - Get a single entry
- [ ] POST entries/\{id\} - Update an entry
- [ ] DELETE /entries/{id} - Delete an entry
- [ ] DELETE /entries - Delete all entries
- [ ] POST /auth/signup - Create new user account
- [ ] POST /auth/login - Authenticate user and get token
- [ ] POST /auth/logout - Invalidate user token
- [ ] POST /auth/forgot-password - Request password reset
- [ ] POST /auth/reset-password - Reset password with token
- [ ] Add request/response validation
- [ ] Add error handling

### 2. Data Model

#### Journal Entry

| Field      | Type     | Validation              |
| ---------- | -------- | ----------------------- |
| id         | string   | Auto-generated UUID     |
| work       | string   | Required, max 256 chars |
| struggle   | string   | Required, max 256 chars |
| intention  | string   | Required, max 256 chars |
| created_at | datetime | Auto-generated UTC      |
| updated_at | datetime | Auto-updated UTC        |

#### User

| Field            | Type     | Validation                    |
| ---------------- | -------- | ----------------------------- |
| id               | string   | Auto-generated UUID           |
| email            | string   | Required, valid email format  |
| password         | string   | Required, min 8 chars, hashed |
| reset_token      | string   | Optional                      |
| token_expires_at | datetime | Optional                      |
| created_at       | datetime | Auto-generated UTC            |

### 3. Testing the API

Test implementation using these curl commands:

```bash
# Create a journal entry (requires auth token)
curl -X POST http://localhost:8000/entries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "work": "Learned FastAPI basics",
    "struggle": "Understanding async/await",
    "intention": "Practice more with FastAPI"
  }'
```

```bash
# Get all entries (requires auth token)
curl -X GET http://localhost:8000/entries \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Get single entry (requires auth token)
curl -X GET http://localhost:8000/entries/{id} \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Update an entry (requires auth token)
curl -X PUT http://localhost:8000/entries/{id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "work": "Updated work entry",
    "struggle": "Updated struggle",
    "intention": "Updated intention"
  }'
```

```bash
# Delete an entry (requires auth token)
curl -X DELETE http://localhost:8000/entries/{id} \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Delete all entries (requires auth token)
curl -X DELETE http://localhost:8000/entries \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

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
# Logout (requires auth token)
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

```bash
# Forgot Password Reset
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

Note: Replace `YOUR_ACCESS_TOKEN` with the actual JWT token received from the login endpoint.

## API Documentation

Once running, API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
