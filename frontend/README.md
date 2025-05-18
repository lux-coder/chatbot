# Frontend Service

Next.js based frontend for the Secure Chatbot Application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
- Copy `.env.example` to `.env.local`
- Update the variables as needed

## Development

```bash
npm run dev
```

## Security Features

- Keycloak integration for authentication
- CSRF protection
- XSS prevention
- Secure HTTP headers
- Input validation

## Project Structure

```
frontend/
├── components/         # React components
│   ├── auth/          # Authentication components
│   ├── chat/          # Chat interface components
│   └── common/        # Shared components
├── pages/             # Next.js pages
│   ├── auth/          # Authentication pages
│   └── chat/          # Chat application pages
├── lib/               # Utility functions
│   ├── auth/          # Authentication utilities
│   └── api/           # API client
└── config/            # Configuration files
```

## Dependencies

- Next.js
- React
- Keycloak-js
- Axios
- React-Query 