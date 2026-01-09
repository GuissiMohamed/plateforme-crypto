# backend/auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import User, get_db
from schemas import TokenData

# ============================================================
# CONFIG JWT
# ============================================================

SECRET_KEY = "super_secret_key_change_me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================
# PASSWORD HASHING (bcrypt safe)
# ============================================================

def _bcrypt_safe_secret(secret: str) -> str:
    """
    bcrypt limite le mot de passe à 72 BYTES (pas 72 caractères).
    Donc on tronque en bytes UTF-8, puis on redécode.
    """
    if not secret:
        return ""
    b = secret.strip().encode("utf-8")
    b = b[:72]
    return b.decode("utf-8", errors="ignore")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(_bcrypt_safe_secret(password))

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_bcrypt_safe_secret(plain), hashed)

# ============================================================
# TOKEN CREATION
# ============================================================

def create_access_token(data: dict, expires: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ============================================================
# USER HELPERS
# ============================================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ============================================================
# CURRENT USER
# ============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise exception
    except JWTError:
        raise exception

    user = get_user_by_email(db, email)
    if not user:
        raise exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
