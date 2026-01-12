"""FastAPI application for PKI-based 2FA microservice."""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

from crypto_utils import (
    load_private_key,
    decrypt_seed,
    generate_totp_code,
    get_totp_remaining_seconds,
    verify_totp_code
)
from config import STUDENT_PRIVATE_KEY_PATH, SEED_FILE_PATH, API_HOST, API_PORT

app = FastAPI(title="PKI-based 2FA Microservice")

# Load student private key at startup
try:
    student_private_key = load_private_key(STUDENT_PRIVATE_KEY_PATH)
except Exception as e:
    print(f"Warning: Could not load student private key: {e}")
    student_private_key = None


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str


@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: DecryptSeedRequest) -> Dict[str, str]:
    """
    Decrypt encrypted seed and store persistently.
    
    Request: {"encrypted_seed": "base64..."}
    Success: {"status": "ok"} (200)
    Failure: {"error": "Decryption failed"} (500)
    """
    try:
        if student_private_key is None:
            raise HTTPException(status_code=500, detail={"error": "Private key not loaded"})
        
        # Decrypt the seed
        hex_seed = decrypt_seed(request.encrypted_seed, student_private_key)
        
        # Ensure /data directory exists
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
        
        # Save to persistent storage
        with open(SEED_FILE_PATH, 'w') as f:
            f.write(hex_seed)
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Decryption error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Decryption failed"})


@app.get("/generate-2fa")
async def generate_2fa_endpoint() -> Dict:
    """
    Generate current TOTP code and calculate remaining validity.
    
    Success: {"code": "123456", "valid_for": 30} (200)
    Failure: {"error": "Seed not decrypted yet"} (500)
    """
    try:
        # Check if seed file exists
        if not os.path.exists(SEED_FILE_PATH):
            raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
        
        # Read hex seed from persistent storage
        with open(SEED_FILE_PATH, 'r') as f:
            hex_seed = f.read().strip()
        
        # Generate TOTP code
        code = generate_totp_code(hex_seed)
        
        # Calculate remaining seconds in current period
        valid_for = get_totp_remaining_seconds()
        
        return {
            "code": code,
            "valid_for": valid_for
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"TOTP generation error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})


@app.post("/verify-2fa")
async def verify_2fa_endpoint(request: VerifyCodeRequest) -> Dict[str, bool]:
    """
    Verify TOTP code with ±1 period tolerance.
    
    Request: {"code": "123456"}
    Success: {"valid": true/false} (200)
    Missing code: {"error": "Missing code"} (400)
    No seed: {"error": "Seed not decrypted yet"} (500)
    """
    try:
        # Validate code is provided
        if not request.code:
            raise HTTPException(status_code=400, detail={"error": "Missing code"})
        
        # Check if seed file exists
        if not os.path.exists(SEED_FILE_PATH):
            raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
        
        # Read hex seed from persistent storage
        with open(SEED_FILE_PATH, 'r') as f:
            hex_seed = f.read().strip()
        
        # Verify TOTP code with ±1 period tolerance
        is_valid = verify_totp_code(hex_seed, request.code)
        
        return {"valid": is_valid}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"TOTP verification error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container readiness."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
