"""
JWT authentication and password hashing utilities.
Uses custom HS256 JWT implementation to avoid cryptography dependency issues.
"""

from datetime import datetime, timedelta
from typing import Optional
import os
import hashlib
import hmac
import base64
import json

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import get_db
from . import models, schemas

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Password hashing iterations (PBKDF2-like approach using SHA-256)
HASH_ITERATIONS = 100000

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _base64url_encode(data: bytes) -> str:
    """Base64 URL-safe encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Base64 URL-safe decoding with padding restoration."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def _create_signature(message: str, secret: str) -> str:
    """Create HMAC-SHA256 signature."""
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return _base64url_encode(signature)


def _hash_password_with_salt(password: str, salt: str) -> str:
    """Hash password with salt using PBKDF2-like iterations."""
    result = password + salt
    for _ in range(HASH_ITERATIONS):
        result = hashlib.sha256(result.encode('utf-8')).hexdigest()
    return result


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        # Format: salt$hash
        salt, stored_hash = hashed_password.split('$')
        computed_hash = _hash_password_with_salt(plain_password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password for storage with random salt."""
    salt = secrets.token_hex(16)
    password_hash = _hash_password_with_salt(password, salt)
    return f"{salt}${password_hash}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token using HS256.

    Args:
        data: Dictionary with claims to encode (must include "sub" for username)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire.timestamp()})

    # Create JWT manually (HS256)
    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_encoded = _base64url_encode(json.dumps(to_encode, separators=(',', ':')).encode('utf-8'))

    message = f"{header_encoded}.{payload_encoded}"
    signature = _create_signature(message, SECRET_KEY)

    return f"{message}.{signature}"


def decode_token(token: str) -> Optional[schemas.TokenData]:
    """
    Decode and validate a JWT token.

    Returns:
        TokenData with username if valid, None otherwise
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header_encoded, payload_encoded, signature = parts

        # Verify signature
        message = f"{header_encoded}.{payload_encoded}"
        expected_signature = _create_signature(message, SECRET_KEY)

        if not hmac.compare_digest(signature, expected_signature):
            return None

        # Decode payload
        payload_json = _base64url_decode(payload_encoded)
        payload = json.loads(payload_json)

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None

        username = payload.get("sub")
        if username is None:
            return None

        return schemas.TokenData(username=username)

    except Exception:
        return None


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user by username and password.

    Returns:
        User object if credentials are valid, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    """
    Create a new user in the database.

    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if get_user_by_username(db, user_data.username):
        raise ValueError("Username already registered")

    # Check if email exists
    if get_user_by_email(db, user_data.email):
        raise ValueError("Email already registered")

    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Initialize first module as unlocked for each book
    for book_id in range(1, 11):  # 10 books
        progress = models.UserProgress(
            user_id=db_user.id,
            book_id=book_id,
            module_id=1,
            is_unlocked=True  # First module always unlocked
        )
        db.add(progress)

    db.commit()

    return db_user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get current authenticated user from JWT token.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception

    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )

    return user
