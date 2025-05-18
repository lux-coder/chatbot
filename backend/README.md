# Backend Service

FastAPI based backend for the Secure Chatbot Application.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the variables as needed

## Development

```bash
uvicorn app.main:app --reload
```

## Security Features

- JWT authentication with Keycloak
- SQL injection prevention
- Input validation with Pydantic
- Rate limiting
- CORS protection
- Audit logging

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   │   └── v1/        # API version 1
│   ├── core/          # Core functionality
│   │   ├── security/  # Security configurations
│   │   ├── config.py  # App settings
│   │   └── events.py  # Startup/shutdown events
│   ├── models/        # Database models
│   └── services/      # Business logic
└── tests/             # Test suite
```

## Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- Python-Jose
- Passlib
- Alembic 