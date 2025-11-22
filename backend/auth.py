# backend/auth.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import SessionLocal, User
from schemas import TokenData, UserCreate, UserOut

# ============================================================
# CONFIGURATION JWT
# ============================================================

SECRET_KEY = "change_me_in_production_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================
# DATABASE session
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# PASSWORD HASHING (FIX BCRYPT 72 bytes)
# ============================================================

def get_password_hash(password: str) -> str:
    # Protection contre les espaces invisibles / \n / \r
    password = password.strip()

    # Limite bcrypt : 72 bytes → obligatoire !
    password = password[:72]

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password.strip()
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================
# JWT TOKEN CREATION
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
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
# CURRENT USER (JWT)
# ============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)

    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, token_data.email)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:

        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        return current_user
