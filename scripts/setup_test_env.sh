#!/bin/bash

# Create test database user and grant privileges
sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
        CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';
    END IF;
END
\$\$;

ALTER USER postgres WITH SUPERUSER;
EOF

# Install test dependencies
pip install -r requirements.txt
pip install pytest-asyncio pytest-cov pytest-env

# Create test .env file if it doesn't exist
if [ ! -f .env.test ]; then
    cat > .env.test << EOL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=test_chatbot_db

# Pool Settings
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=10

# Tenant Settings
SCHEMA_PREFIX=tenant_
EOL
    echo ".env.test file created successfully"
else
    echo ".env.test file already exists"
fi

echo "Test environment setup completed successfully" 