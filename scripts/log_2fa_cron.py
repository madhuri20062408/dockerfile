#!/usr/bin/env python3
"""Cron script to log 2FA codes every minute."""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_utils import generate_totp_code
from config import SEED_FILE_PATH


def main():
    """Generate and log current TOTP code."""
    try:
        # Read hex seed from persistent storage
        if not os.path.exists(SEED_FILE_PATH):
            print(f"Error: Seed file not found at {SEED_FILE_PATH}", file=sys.stderr)
            return
        
        with open(SEED_FILE_PATH, 'r') as f:
            hex_seed = f.read().strip()
        
        # Generate current TOTP code
        code = generate_totp_code(hex_seed)
        
        # Get current UTC timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Output formatted line (appended by cron to /cron/last_code.txt)
        print(f"{timestamp} - 2FA Code: {code}")
    
    except Exception as e:
        print(f"Error generating TOTP code: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
