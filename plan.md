# Journal API Implementation Plan

## 1. Project Setup and Structure

``` sturcture
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

## 2. Technical Stack

- **Core Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy
- **Security**: Python-Jose (JWT), Passlib (bcrypt)
- **Validation**: Pydantic v2
- **Testing**: Pytest
- **Development Tools**: Black (formatting), Flake8 (linting), isort (import sorting)

## 3. Implementation Phases

### Phase 1: Setup & Configuration

- [x] Project structure setup ✅
- [x] Dependencies installation ✅
- [x] Environment configuration ✅
- [x] Database connection setup ✅
- [x] Basic FastAPI app setup ✅
- [x] FastAPI lifespan events setup ✅

### Phase 2: Database Models

- [x] Create User model ✅
  - UUID primary key ✅
  - Email field (unique) ✅
  - Hashed password field ✅
  - Reset token fields ✅
  - Timestamps ✅
- [x] Create Journal Entry model ✅
  - UUID primary key ✅
  - Foreign key to User ✅
  - Work, struggle, intention fields ✅
  - Timestamps ✅

### Phase 3: Authentication System

- [x] User registration endpoint ✅
- [x] Login endpoint with JWT token ✅
- [x] Password hashing implementation ✅
- [x] JWT token validation ✅
- [x] Protected route middleware ✅
- [x] Logout mechanism ✅
- [x] Password reset flow ✅
- [x] Token refresh mechanism ✅
- [x] Comprehensive test suite ✅

### Phase 4: Journal Entry API

- [x] Create entry endpoint ✅
- [x] Get all entries endpoint ✅
- [x] Get single entry endpoint ✅
- [x] Update entry endpoint ✅
- [x] Delete entry endpoint ✅
- [x] Delete all entries endpoint ✅
- [x] User-specific entry filtering ✅

### Phase 5: Request/Response Models

- [x] User schemas ✅
  - Registration schema ✅
  - Login schema ✅
  - Password reset schema ✅
- [x] Journal entry schemas ✅
  - Create/Update schema ✅
  - Response schema ✅
- [x] Error response schemas ✅

### Phase 6: Security & Error Handling

- [x] Global error handlers ✅
- [x] Input validation ✅
- [x] Rate limiting ✅
- [x] CORS configuration ✅
- [x] Security headers ✅

### Phase 7: Testing

- [x] Unit tests setup ✅
- [x] Authentication tests ✅
  - Registration tests ✅
  - Login tests ✅
  - Token refresh tests ✅
  - Password reset tests ✅
- [x] Journal entry CRUD tests ✅
  - Create entry tests ✅
  - Read entry tests ✅
  - Update entry tests ✅
  - Delete entry tests ✅
  - Authorization tests ✅
- [x] Test database fixtures ✅
- [x] Test mocking (email service) ✅

### Phase 8: Code Quality & Documentation

- [x] API documentation ✅
- [x] Code comments ✅
- [x] Type hints ✅
- [x] Linting configuration ✅
- [x] Code formatting ✅

## 4. API Endpoints

### Authentication Endpoints

``` RestAPI
POST /auth/signup         # ✅ Implemented & Tested
POST /auth/login         # ✅ Implemented & Tested
POST /auth/logout        # ✅ Implemented & Tested
POST /auth/refresh       # ✅ Implemented & Tested
POST /auth/forgot-password # ✅ Implemented & Tested
POST /auth/reset-password  # ✅ Implemented & Tested
```

### Journal Entry Endpoints

``` RestAPI
POST   /entries           # ✅ Implemented & Tested
GET    /entries           # ✅ Implemented & Tested
GET    /entries/{id}      # ✅ Implemented & Tested
PUT    /entries/{id}      # ✅ Implemented & Tested
DELETE /entries/{id}      # ✅ Implemented & Tested
DELETE /entries           # ✅ Implemented & Tested
```

## 5. Database Schema

### Users Table

| Field            | Type                     | Constraints                              |
| ---------------- | ------------------------ | ---------------------------------------- |
| id               | UUID                     | Primary Key, Not Null, Auto-generated    |
| email            | VARCHAR(255)             | Not Null, Unique, Valid Email Format     |
| password         | VARCHAR(255)             | Not Null, Min 8 chars, Hashed            |
| reset_token      | VARCHAR(255)             | Nullable                                 |
| token_expires_at | TIMESTAMP WITH TIME ZONE | Nullable                                 |
| created_at       | TIMESTAMP WITH TIME ZONE | Not Null, Default: now(), Auto-generated |
| updated_at       | TIMESTAMP WITH TIME ZONE | Not Null, Default: now(), Auto-updated   |

SQL Definition:

```sql
CREATE TABLE "user" (
    id UUID NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    reset_token VARCHAR(255),
    token_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ix_user_email ON "user" (email);
```

### Journal Entries Table

| Field      | Type                     | Constraints                               |
| ---------- | ------------------------ | ----------------------------------------- |
| id         | UUID                     | Primary Key, Not Null, Auto-generated     |
| user_id    | UUID                     | Foreign Key -> user.id, Not Null, Indexed |
| work       | VARCHAR(256)             | Not Null, Max: 256 chars                  |
| struggle   | VARCHAR(256)             | Not Null, Max: 256 chars                  |
| intention  | VARCHAR(256)             | Not Null, Max: 256 chars                  |
| created_at | TIMESTAMP WITH TIME ZONE | Not Null, Default: now(), Auto-generated  |
| updated_at | TIMESTAMP WITH TIME ZONE | Not Null, Default: now(), Auto-updated    |

SQL Definition:
```sql
CREATE TABLE journalentry (
    id UUID NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    work VARCHAR(256) NOT NULL,
    struggle VARCHAR(256) NOT NULL,
    intention VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX ix_journalentry_user_id ON journalentry (user_id);
```

## 6. Development Workflow

1. Create feature branch
2. Implement feature/fix
3. Run tests (`make test`)
4. Format code (`make format`)
5. Run linting (`make lint`)
6. Commit changes
7. Create pull request

## 7. Next Steps

1. ✅ Set up local PostgreSQL database
2. ✅ Implement User model and authentication
3. ✅ Create journal entry model and CRUD operations
4. ✅ Add tests for implemented features
5. ✅ Create a script to run and create all database related queries while setup and maybe later when needed.
