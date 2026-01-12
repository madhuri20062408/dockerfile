"""Configuration constants for PKI-based 2FA microservice."""

import os

# File paths
STUDENT_PRIVATE_KEY_PATH = os.getenv("STUDENT_PRIVATE_KEY_PATH", "/app/student_private.pem")
STUDENT_PUBLIC_KEY_PATH = os.getenv("STUDENT_PUBLIC_KEY_PATH", "/app/student_public.pem")
INSTRUCTOR_PUBLIC_KEY_PATH = os.getenv("INSTRUCTOR_PUBLIC_KEY_PATH", "/app/instructor_public.pem")
SEED_FILE_PATH = os.getenv("SEED_FILE_PATH", "/data/seed.txt")
CRON_OUTPUT_PATH = os.getenv("CRON_OUTPUT_PATH", "/cron/last_code.txt")

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8080

# Instructor API
INSTRUCTOR_API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# RSA configuration
RSA_KEY_SIZE = 4096
RSA_PUBLIC_EXPONENT = 65537

# TOTP configuration
TOTP_ALGORITHM = "SHA1"  # Standard for TOTP
TOTP_PERIOD = 30  # seconds
TOTP_DIGITS = 6
TOTP_VALID_WINDOW = 1  # ±1 period (±30 seconds)
