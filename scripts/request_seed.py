#!/usr/bin/env python3
"""Request encrypted seed from instructor API."""

import sys
import os
import requests
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import INSTRUCTOR_API_URL


def main():
    """Request encrypted seed from instructor API."""
    if len(sys.argv) != 3:
        print("Usage: python request_seed.py <student_id> <github_repo_url>")
        print("\nExample:")
        print("  python request_seed.py S12345 https://github.com/username/repo-name")
        sys.exit(1)
    
    student_id = sys.argv[1]
    github_repo_url = sys.argv[2]
    
    print(f"Student ID: {student_id}")
    print(f"GitHub Repository URL: {github_repo_url}")
    print(f"\n⚠️  CRITICAL: Use the EXACT same repository URL in your submission!")
    
    # Read student public key
    public_key_path = "student_public.pem"
    if not os.path.exists(public_key_path):
        print(f"\n❌ Error: {public_key_path} not found!")
        print("   Run 'python scripts/generate_keys.py' first.")
        sys.exit(1)
    
    with open(public_key_path, 'r') as f:
        public_key = f.read()
    
    # Prepare request payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key
    }
    
    print(f"\nCalling instructor API: {INSTRUCTOR_API_URL}")
    
    try:
        # Send POST request
        response = requests.post(
            INSTRUCTOR_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        if result.get("status") == "success" and "encrypted_seed" in result:
            encrypted_seed = result["encrypted_seed"]
            
            # Save encrypted seed to file
            with open("encrypted_seed.txt", 'w') as f:
                f.write(encrypted_seed)
            
            print("\n✓ Success! Encrypted seed received and saved to: encrypted_seed.txt")
            print(f"  Encrypted seed length: {len(encrypted_seed)} characters")
            print("\n⚠️  DO NOT commit encrypted_seed.txt to Git!")
        else:
            print(f"\n❌ Error: Unexpected response format")
            print(f"Response: {json.dumps(result, indent=2)}")
            sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error calling instructor API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
