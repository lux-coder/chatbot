# AI Service

AI integration service supporting both OpenAI and Llama.cpp for the Secure Chatbot Application.

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
- Add your OpenAI API key
- Configure Llama.cpp paths

4. Download Llama.cpp model:
```bash
# Instructions for downloading and setting up Llama model will be here
```

## Development

```bash
python -m ai_service.main
```

## Security Features

- Input sanitization
- Prompt injection prevention
- Response validation
- Rate limiting
- Model output filtering

## Project Structure

```
ai_service/
├── models/
│   ├── openai/        # OpenAI integration
│   └── llama/         # Llama.cpp integration
├── security/          # Security measures
└── utils/            # Utility functions
```

## Dependencies

- OpenAI Python
- Llama.cpp Python bindings
- TensorFlow/PyTorch (if needed)
- Transformers 