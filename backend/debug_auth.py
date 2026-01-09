"""Test ultra simple pour déboguer l'auth"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from jose import jwt
from datetime import datetime, timedelta, timezone

# ===== DB SETUP =====
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DummyUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

# ===== AUTH SETUP =====
SECRET_KEY = "test_secret"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    print(f"[DEBUG] Token received: {token[:20]}...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG] Decoded payload: {payload}")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="No email in token")
    except Exception as e:
        print(f"[DEBUG] JWT decode error: {e}")
        raise HTTPException(status_code=401, detail=f"JWT error: {str(e)}")
    
    user = db.query(DummyUser).filter_by(email=email).first()
    print(f"[DEBUG] User found in DB: {user}")
    if not user:
        raise HTTPException(status_code=401, detail="User not in DB")
    return user

# ===== APP =====
app = FastAPI()

@app.post("/login")
def login(db = Depends(get_db)):
    # Create a test user
    user = DummyUser(email="test@example.com")
    db.add(user)
    db.commit()
    
    # Create a token
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}

@app.get("/protected")
async def protected(user: DummyUser = Depends(get_current_user)):
    return {"email": user.email}

# ===== TEST =====
client = TestClient(app)

# Login
print("[TEST] Logging in...")
response = client.post("/login")
print(f"[TEST] Login response: {response.status_code}")
token = response.json()["access_token"]
print(f"[TEST] Token: {token[:30]}...")

# Try protected endpoint
print("[TEST] Calling /protected...")
response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
print(f"[TEST] Protected response: {response.status_code}")
print(f"[TEST] Protected body: {response.json()}")
