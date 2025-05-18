# Worker Service

Celery-based background worker for the Secure Chatbot Application.

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
- Update Redis connection settings

## Development

Start Celery worker:
```bash
celery -A worker.main worker --loglevel=info
```

## Features

- Asynchronous task processing
- Task monitoring and logging
- Error handling and retries
- Rate limiting
- Task prioritization

## Project Structure

```
worker/
├── tasks/             # Celery tasks
│   ├── chat.py        # Chat processing tasks
│   └── audit.py       # Audit logging tasks
├── config/            # Configuration
└── utils/             # Utility functions
```

## Dependencies

- Celery
- Redis
- Flower (for monitoring)
- SQLAlchemy 