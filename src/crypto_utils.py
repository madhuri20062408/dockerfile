"""Cryptographic utilities for RSA and TOTP operations."""

import base64
import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from typing import Tuple

from config import RSA_KEY_SIZE, RSA_PUBLIC_EXPONENT, TOTP_DIGITS, TOTP_PERIOD, TOTP_VALID_WINDOW


def generate_rsa_keypair(key_size: int = RSA_KEY_SIZE) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generate RSA key pair with specified key size.
    
    Args:
        key_size: RSA key size in bits (default: 4096)
    
    Returns:
        Tuple of (private_key, public_key) objects
    """
    private_key = rsa.generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_private_key(private_key: rsa.RSAPrivateKey, filepath: str) -> None:
    """Save private key to PEM file."""
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filepath, 'wb') as f:
        f.write(pem)


def save_public_key(public_key: rsa.RSAPublicKey, filepath: str) -> None:
    """Save public key to PEM file."""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filepath, 'wb') as f:
        f.write(pem)


def load_private_key(filepath: str) -> rsa.RSAPrivateKey:
    """Load private key from PEM file."""
    with open(filepath, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def load_public_key(filepath: str) -> rsa.RSAPublicKey:
    """Load public key from PEM file."""
    with open(filepath, 'rb') as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )
    return public_key


def decrypt_seed(encrypted_seed_b64: str, private_key: rsa.RSAPrivateKey) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256.
    
    Args:
        encrypted_seed_b64: Base64-encoded ciphertext
        private_key: RSA private key object
    
    Returns:
        Decrypted hex seed (64-character string)
    
    Raises:
        ValueError: If decrypted seed is not valid 64-character hex string
    """
    # Base64 decode the encrypted seed
    encrypted_seed_bytes = base64.b64decode(encrypted_seed_b64)
    
    # RSA/OAEP decrypt with SHA-256
    decrypted_bytes = private_key.decrypt(
        encrypted_seed_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Decode bytes to UTF-8 string
    hex_seed = decrypted_bytes.decode('utf-8')
    
    # Validate: must be 64-character hex string
    if len(hex_seed) != 64:
        raise ValueError(f"Invalid seed length: {len(hex_seed)}, expected 64")
    
    if not all(c in '0123456789abcdef' for c in hex_seed.lower()):
        raise ValueError("Seed contains non-hexadecimal characters")
    
    return hex_seed


def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 encoding for TOTP.
    
    Args:
        hex_seed: 64-character hex string
    
    Returns:
        Base32-encoded seed string
    """
    # Convert hex to bytes
    seed_bytes = bytes.fromhex(hex_seed)
    
    # Convert bytes to base32
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.
    
    Args:
        hex_seed: 64-character hex string
    
    Returns:
        6-digit TOTP code as string
    """
    # Convert hex seed to base32
    base32_seed = hex_to_base32(hex_seed)
    
    # Create TOTP object with SHA-1, 30s period, 6 digits (standard)
    totp = pyotp.TOTP(base32_seed, digits=TOTP_DIGITS, interval=TOTP_PERIOD)
    
    # Generate current TOTP code
    code = totp.now()
    
    return code


def get_totp_remaining_seconds() -> int:
    """
    Calculate remaining seconds in current TOTP period.
    
    Returns:
        Remaining seconds (0-29)
    """
    import time
    current_time = int(time.time())
    remaining = TOTP_PERIOD - (current_time % TOTP_PERIOD)
    return remaining


def verify_totp_code(hex_seed: str, code: str, valid_window: int = TOTP_VALID_WINDOW) -> bool:
    """
    Verify TOTP code with time window tolerance.
    
    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: Number of periods before/after to accept (default 1 = ±30s)
    
    Returns:
        True if code is valid, False otherwise
    """
    # Convert hex seed to base32
    base32_seed = hex_to_base32(hex_seed)
    
    # Create TOTP object
    totp = pyotp.TOTP(base32_seed, digits=TOTP_DIGITS, interval=TOTP_PERIOD)
    
    # Verify code with time window tolerance
    is_valid = totp.verify(code, valid_window=valid_window)
    
    return is_valid


def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256.
    
    Args:
        message: Message to sign (commit hash as ASCII string)
        private_key: RSA private key object
    
    Returns:
        Signature bytes
    """
    # Encode message as UTF-8 bytes (CRITICAL: sign ASCII string, not binary hex!)
    message_bytes = message.encode('utf-8')
    
    # Sign using RSA-PSS with SHA-256 and maximum salt length
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return signature


def encrypt_with_public_key(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256 and public key.
    
    Args:
        data: Data to encrypt (signature bytes)
        public_key: RSA public key object
    
    Returns:
        Encrypted ciphertext bytes
    """
    # Encrypt using RSA/OAEP with SHA-256
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return ciphertext
