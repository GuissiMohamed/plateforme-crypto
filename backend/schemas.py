# backend/schemas.py

from datetime import datetime
from pydantic import BaseModel


class AssetBase(BaseModel):
    id: str
    symbol: str
    name: str


class AssetOut(AssetBase):
    class Config:
        orm_mode = True  # permet de convertir depuis un objet SQLAlchemy


class PriceOut(BaseModel):
    id: int
    asset_id: str
    price_usd: float | None = None
    market_cap_usd: float | None = None
    volume_24h_usd: float | None = None
    change_24h_pct: float | None = None
    timestamp: datetime

    class Config:
        orm_mode = True


class IndicatorOut(BaseModel):
    asset_id: str
    current_price: float | None = None
    ma_short: float | None = None
    ma_long: float | None = None
    change_24h_pct: float | None = None
    signal: str | None = None  # ex: "bullish", "bearish", "neutral"

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str | None = None

class TransactionCreate(BaseModel):
    asset_id: str
    quantity: float


class TransactionOut(BaseModel):
    id: int
    asset_id: str
    quantity: float
    price_usd: float
    is_buy: bool
    timestamp: datetime

    class Config:
        from_attributes = True


