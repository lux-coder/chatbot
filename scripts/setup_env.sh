#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOL
# Database Settings
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chatbot_db

# Pool Settings
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10

# Tenant Settings
SCHEMA_PREFIX=tenant_
EOL
    echo ".env file created successfully"
else
    echo ".env file already exists"
fi

# Create virtual environment if it doesn't exist
if [ ! -d .venv ]; then
    python3.12 -m venv .venv
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment and install requirements
source .venv/bin/activate
pip install -r requirements.txt

echo "Setup completed successfully" 