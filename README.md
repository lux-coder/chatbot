# Secure Chatbot Application

This project is an academic demonstration for a secure web application as part of postgraduate studies. It implements a chatbot service with both OpenAI and Llama.cpp integration, focusing on security best practices.

## Prerequisites

- Docker and Docker Compose
- Node.js (for frontend development)
- Python 3.8+
- PostgreSQL
- Redis
- Keycloak

## Project Structure

See `plans/implementation_plan.md` for detailed project structure and implementation phases.

## Setup Instructions

1. Clone the repository
2. Copy `.env.example` to `.env` and configure environment variables
3. Run `docker-compose up` to start the development environment
4. Follow service-specific setup instructions in their respective directories

## Development

Each service has its own README with specific development instructions:

- Frontend: `frontend/README.md`
- Backend: `backend/README.md`
- Worker: `worker/README.md`
- AI Service: `ai_service/README.md`

## Security Features

This application implements various security features:
- Keycloak Authentication
- JWT Token Handling
- WAF Protection
- Input Validation
- XSS Protection
- CSRF Protection
- Rate Limiting
- Audit Logging

## License

Academic Use Only