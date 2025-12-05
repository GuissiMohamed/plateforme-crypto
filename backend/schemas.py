# backend/schemas.py

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# ========================
# ASSETS & PRICES
# ========================

class AssetOut(BaseModel):
    id: str
    symbol: str
    name: str

    class Config:
        orm_mode = True


class PriceOut(BaseModel):
    id: int
    asset_id: str
    price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    change_24h_pct: Optional[float] = None
    timestamp: datetime

    class Config:
        orm_mode = True


# ========================
# INDICATORS
# ========================

class IndicatorOut(BaseModel):
    asset_id: str
    current_price: Optional[float] = None

    ma_short: Optional[float] = None
    ma_long: Optional[float] = None

    ema_short: Optional[float] = None
    ema_long: Optional[float] = None

    rsi: Optional[float] = None

    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None

    change_24h_pct: Optional[float] = None
    signal: str


# ========================
# USERS & AUTH
# ========================

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    role: str

    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# 🆕 Mises à jour du profil

class UserUpdateEmail(BaseModel):
    new_email: EmailStr
    password: str


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdateProfile(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class DiscordWebhookUpdate(BaseModel):
    discord_webhook_url: Optional[str] = None  # None = supprimer


# ========================
# PORTFOLIO & TRANSACTIONS
# ========================

class TransactionCreate(BaseModel):
    asset_id: str
    quantity: float


class TransactionOut(BaseModel):
    id: int
    user_id: int
    asset_id: str
    quantity: float
    price_usd: float
    is_buy: bool
    timestamp: datetime

    class Config:
        orm_mode = True


# ========================
# ALERTS & NOTIFICATIONS
# ========================

class AlertCreate(BaseModel):
    asset_id: str
    alert_type: str  # "above", "below", "change_24h"
    target_value: float


class AlertOut(BaseModel):
    id: int
    user_id: int
    asset_id: str
    alert_type: str
    target_value: float
    triggered: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True
