#!/bin/bash

# Set variables
CERT_DIR="nginx/certs"
DAYS_VALID=365
COUNTRY="US"
STATE="State"
LOCALITY="City"
ORGANIZATION="Organization"
ORGANIZATIONAL_UNIT="Development"
COMMON_NAME="localhost"
EMAIL="admin@example.com"

# Generate RSA private key
openssl genrsa -out ${CERT_DIR}/server.key 4096

# Generate Certificate Signing Request (CSR)
openssl req -new -key ${CERT_DIR}/server.key -out ${CERT_DIR}/server.csr -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=${COMMON_NAME}/emailAddress=${EMAIL}"

# Generate self-signed certificate
openssl x509 -req -days ${DAYS_VALID} \
    -in ${CERT_DIR}/server.csr \
    -signkey ${CERT_DIR}/server.key \
    -out ${CERT_DIR}/server.crt \
    -sha256

# Set proper permissions
chmod 600 ${CERT_DIR}/server.key
chmod 644 ${CERT_DIR}/server.crt

# Clean up CSR
rm ${CERT_DIR}/server.csr

echo "SSL certificates generated successfully in ${CERT_DIR}/"
echo "Note: These are self-signed certificates for development only."
echo "For production, use certificates from a trusted CA." 