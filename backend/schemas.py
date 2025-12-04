# backend/schemas.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


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
    current_price: Optional[float] = None

    # Moyennes mobiles simples
    ma_short: Optional[float] = None
    ma_long: Optional[float] = None

    # Moyennes mobiles exponentielles
    ema_short: Optional[float] = None
    ema_long: Optional[float] = None

    # RSI
    rsi: Optional[float] = None

    # MACD
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None

    # Variation et signal global
    change_24h_pct: Optional[float] = None
    signal: Optional[str] = None

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


