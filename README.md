# PKI-Based 2FA Microservice

A secure, containerized microservice implementing RSA 4096-bit PKI and TOTP-based two-factor authentication with persistent storage and automated cron jobs.

## Features

- **RSA 4096-bit Encryption**: Secure seed transmission using RSA/OAEP with SHA-256
- **TOTP 2FA**: Time-based one-time password authentication with ±30s tolerance
- **REST API**: Three endpoints for seed decryption, code generation, and verification
- **Docker Containerization**: Multi-stage build with persistent volumes
- **Automated Cron Jobs**: Minute-by-minute TOTP code logging
- **UTC Timezone**: All operations use UTC for consistency

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local scripts)
- Git
- GitHub account and repository

## Quick Start

### 1. Generate Student Key Pair

```bash
python scripts/generate_keys.py
```

This creates:
- `student_private.pem` - Your RSA private key (will be committed to Git)
- `student_public.pem` - Your RSA public key (will be committed to Git)

⚠️ **WARNING**: These keys will be PUBLIC in your repository. DO NOT reuse them!

### 2. Download Instructor Public Key

Download `instructor_public.pem` from course resources and place it in the project root.

### 3. Request Encrypted Seed

```bash
python scripts/request_seed.py <STUDENT_ID> <GITHUB_REPO_URL>
```

Example:
```bash
python scripts/request_seed.py S12345 https://github.com/username/pki-2fa-microservice
```

⚠️ **CRITICAL**: Use the EXACT same GitHub repository URL in your submission!

This creates `encrypted_seed.txt` (NOT committed to Git).

### 4. Build and Run Docker Container

```bash
docker-compose build
docker-compose up -d
```

### 5. Test API Endpoints

#### Decrypt Seed
```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
```

Expected: `{"status": "ok"}`

#### Generate 2FA Code
```bash
curl http://localhost:8080/generate-2fa
```

Expected: `{"code": "123456", "valid_for": 30}`

#### Verify 2FA Code
```bash
CODE=$(curl -s http://localhost:8080/generate-2fa | jq -r '.code')
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}"
```

Expected: `{"valid": true}`

### 6. Verify Cron Job

Wait 70+ seconds, then check cron output:

```bash
docker exec pki-2fa cat /cron/last_code.txt
```

Expected output:
```
2026-01-12 14:30:00 - 2FA Code: 123456
2026-01-12 14:31:00 - 2FA Code: 789012
```

### 7. Test Container Restart Persistence

```bash
docker-compose restart
sleep 5
curl http://localhost:8080/generate-2fa
```

Seed should persist across restarts.

### 8. Generate Commit Proof

Commit all code to Git, then:

```bash
python scripts/generate_proof.py
```

This outputs:
- Commit hash (40-character hex)
- Encrypted signature (base64, single line)

## Project Structure

```
docker-new/
├── src/
│   ├── app.py              # FastAPI application
│   ├── crypto_utils.py     # Cryptographic operations
│   └── config.py           # Configuration constants
├── scripts/
│   ├── generate_keys.py    # Generate RSA key pair
│   ├── request_seed.py     # Request encrypted seed
│   ├── log_2fa_cron.py     # Cron job script
│   └── generate_proof.py   # Generate commit proof
├── cron/
│   └── 2fa-cron            # Cron configuration (LF line endings!)
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── .gitattributes          # Force LF line endings
├── student_private.pem     # Student RSA private key (COMMITTED)
├── student_public.pem      # Student RSA public key (COMMITTED)
├── instructor_public.pem   # Instructor RSA public key (COMMITTED)
└── encrypted_seed.txt      # Encrypted seed (NOT COMMITTED)
```

## API Endpoints

### POST /decrypt-seed

Decrypt encrypted seed and store persistently.

**Request:**
```json
{
  "encrypted_seed": "base64_encoded_ciphertext"
}
```

**Success Response (200):**
```json
{
  "status": "ok"
}
```

**Error Response (500):**
```json
{
  "error": "Decryption failed"
}
```

### GET /generate-2fa

Generate current TOTP code and calculate remaining validity.

**Success Response (200):**
```json
{
  "code": "123456",
  "valid_for": 30
}
```

**Error Response (500):**
```json
{
  "error": "Seed not decrypted yet"
}
```

### POST /verify-2fa

Verify TOTP code with ±1 period tolerance (±30 seconds).

**Request:**
```json
{
  "code": "123456"
}
```

**Success Response (200):**
```json
{
  "valid": true
}
```

or

```json
{
  "valid": false
}
```

**Error Responses:**
- 400: `{"error": "Missing code"}`
- 500: `{"error": "Seed not decrypted yet"}`

## Cryptographic Specifications

### RSA Key Generation
- Key size: 4096 bits
- Public exponent: 65537
- Format: PEM

### RSA/OAEP Decryption/Encryption
- Padding: OAEP
- MGF: MGF1 with SHA-256
- Hash: SHA-256
- Label: None

### RSA-PSS Signature
- Padding: PSS
- MGF: MGF1 with SHA-256
- Hash: SHA-256
- Salt length: Maximum (PSS.MAX_LENGTH)

### TOTP Configuration
- Algorithm: SHA-1 (standard)
- Period: 30 seconds
- Digits: 6
- Seed format: Hex → Bytes → Base32

## Troubleshooting

### Cron job not running
- Check line endings: `file cron/2fa-cron` should show Unix line endings
- Verify .gitattributes is configured correctly
- Check cron is running: `docker exec pki-2fa ps aux | grep cron`

### TOTP codes don't match
- Verify timezone is UTC: `docker exec pki-2fa date`
- Check seed was decrypted correctly
- Ensure same student_id and github_repo_url used

### Decryption failed
- Verify correct private key is being used
- Check encrypted_seed.txt has no line breaks
- Ensure RSA/OAEP parameters match specifications

### Container won't start
- Check Docker logs: `docker-compose logs`
- Verify all key files exist
- Rebuild without cache: `docker-compose build --no-cache`

## Security Notes

⚠️ **IMPORTANT**: The student private key is committed to Git and will be PUBLIC. This is required for the assignment but means:
- These keys are compromised once committed
- DO NOT reuse these keys for any other purpose
- Generate new keys for any production use

## License

This project is for educational purposes only.
