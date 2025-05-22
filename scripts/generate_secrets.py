#!/usr/bin/env python3
"""Generate secure secrets for Docker services."""

import secrets
import string
import os
from pathlib import Path

def generate_secure_password(length=32):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def write_secret(name, value):
    """Write a secret to a file."""
    secrets_dir = Path("secrets")
    secrets_dir.mkdir(exist_ok=True)
    
    secret_file = secrets_dir / f"{name}.txt"
    secret_file.write_text(value)
    # Set proper permissions
    os.chmod(secret_file, 0o600)

def main():
    """Generate all required secrets."""
    secrets_to_generate = {
        "postgres_password": 32,
        "redis_password": 32,
        "keycloak_secret": 64,
        "keycloak_admin_password": 32,
        "keycloak_webhook_secret": 64,
    }
    
    for secret_name, length in secrets_to_generate.items():
        password = generate_secure_password(length)
        write_secret(secret_name, password)
        print(f"Generated {secret_name}")
    
    # OpenAI API key needs to be set manually
    write_secret("openai_api_key", "YOUR_OPENAI_API_KEY_HERE")
    print("\nSecrets generated successfully!")
    print("NOTE: Please set your OpenAI API key in scripts/secrets/openai_api_key.txt")

if __name__ == "__main__":
    main() 