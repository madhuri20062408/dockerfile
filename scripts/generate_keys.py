#!/usr/bin/env python3
"""Generate RSA 4096-bit student key pair."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_utils import generate_rsa_keypair, save_private_key, save_public_key


def main():
    """Generate and save RSA key pair."""
    print("Generating RSA 4096-bit key pair...")
    
    # Generate key pair
    private_key, public_key = generate_rsa_keypair()
    
    # Save keys
    private_key_path = "student_private.pem"
    public_key_path = "student_public.pem"
    
    save_private_key(private_key, private_key_path)
    save_public_key(public_key, public_key_path)
    
    print(f"✓ Private key saved to: {private_key_path}")
    print(f"✓ Public key saved to: {public_key_path}")
    print("\n⚠️  WARNING: These keys will be committed to Git and will be PUBLIC!")
    print("   DO NOT reuse these keys for any other purpose.")


if __name__ == "__main__":
    main()
