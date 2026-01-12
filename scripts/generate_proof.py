#!/usr/bin/env python3
"""Generate commit signature proof for submission."""

import sys
import os
import subprocess
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_utils import load_private_key, load_public_key, sign_message, encrypt_with_public_key


def get_commit_hash():
    """Get the latest commit hash."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit hash: {e}")
        sys.exit(1)


def main():
    """Generate commit signature proof."""
    print("Generating commit signature proof...\n")
    
    # Get current commit hash
    commit_hash = get_commit_hash()
    print(f"Commit Hash: {commit_hash}")
    
    # Load student private key
    student_private_key_path = "student_private.pem"
    if not os.path.exists(student_private_key_path):
        print(f"\n❌ Error: {student_private_key_path} not found!")
        sys.exit(1)
    
    student_private_key = load_private_key(student_private_key_path)
    print(f"✓ Loaded student private key")
    
    # Sign commit hash with student private key (RSA-PSS-SHA256)
    signature = sign_message(commit_hash, student_private_key)
    print(f"✓ Signed commit hash with RSA-PSS-SHA256")
    
    # Load instructor public key
    instructor_public_key_path = "instructor_public.pem"
    if not os.path.exists(instructor_public_key_path):
        print(f"\n❌ Error: {instructor_public_key_path} not found!")
        print("   Download the instructor public key from course resources.")
        sys.exit(1)
    
    instructor_public_key = load_public_key(instructor_public_key_path)
    print(f"✓ Loaded instructor public key")
    
    # Encrypt signature with instructor public key (RSA/OAEP-SHA256)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)
    print(f"✓ Encrypted signature with RSA/OAEP-SHA256")
    
    # Base64 encode encrypted signature
    encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode('utf-8')
    
    print("\n" + "="*80)
    print("SUBMISSION DATA")
    print("="*80)
    print(f"\nCommit Hash:")
    print(commit_hash)
    print(f"\nEncrypted Signature (Base64 - SINGLE LINE):")
    print(encrypted_signature_b64)
    print("\n" + "="*80)
    print("\n⚠️  Copy the encrypted signature as a SINGLE LINE (no line breaks!)")


if __name__ == "__main__":
    main()
