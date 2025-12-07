import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration (MVP Style)
# In production, these should be in .env
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_change_me_in_prod_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hardcoded Admin User
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
# Default password: "password123" (hashed)
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH", 
    "$2b$12$WtX6mfVX4VxEPbulH2tBMOCaClPQkEhQDHMlZFn44Z0Y6Z.mZKG96"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
