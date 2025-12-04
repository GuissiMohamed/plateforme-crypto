# backend/main.py

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import (
    SessionLocal,
    init_db,
    Asset,
    Price,
    User,
    PortfolioTransaction,
    Alert,
    Notification,
)

from schemas import (
    AssetOut,
    PriceOut,
    IndicatorOut,
    UserOut,
    Token,
    UserCreate,
    TransactionCreate,
    TransactionOut,
    AlertCreate,
    AlertOut,
    NotificationOut,
)

from auth import (
    get_current_active_user,
    get_current_admin,
    get_password_hash,
    authenticate_user,
    create_access_token,
)


# --------------------------------------------------------------------
# APP + CORS
# --------------------------------------------------------------------
app = FastAPI(
    title="Crypto Market Analytics API",
    version="0.1.0",
    description="API backend pour la plateforme crypto.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------
# DATABASE
# --------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


# --------------------------------------------------------------------
# HEALTH
# --------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------------------------
# AUTH
# --------------------------------------------------------------------
@app.post("/auth/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(401, "Incorrect email or password")

    token = create_access_token({"sub": user.email})
    return Token(access_token=token, token_type="bearer")


@app.get("/users/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


# --------------------------------------------------------------------
# ASSETS
# --------------------------------------------------------------------
@app.get("/assets", response_model=List[AssetOut])
def list_assets(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Asset).order_by(Asset.symbol.asc()).limit(limit).all()


# --------------------------------------------------------------------
# PRICES
# --------------------------------------------------------------------
@app.get("/assets/{asset_id}/prices", response_model=List[PriceOut])
def get_asset_prices(
    asset_id: str,
    limit: int = 100,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    query = db.query(Price).filter(Price.asset_id == asset_id)

    if start:
        query = query.filter(Price.timestamp >= start)
    if end:
        query = query.filter(Price.timestamp <= end)

    prices = query.order_by(Price.timestamp.desc()).limit(limit).all()
    if not prices:
        raise HTTPException(404, "No price data")

    return list(reversed(prices))

@app.get("/assets/{asset_id}/indicators", response_model=IndicatorOut)
def get_asset_indicators(
    asset_id: str,
    window_short: int = 20,
    window_long: int = 50,
    db: Session = Depends(get_db),
):
    """
    Renvoie des indicateurs techniques pour une crypto :

    - current_price : dernier prix connu
    - ma_short / ma_long : moyennes mobiles simples
    - ema_short / ema_long : moyennes mobiles exponentielles (12/26)
    - rsi : Relative Strength Index (14 périodes)
    - macd, macd_signal, macd_hist : MACD 12/26/9
    - change_24h_pct : variation sur 24h (depuis la dernière ligne Price)
    - signal : "bullish" / "bearish" / "neutral"
    """

    # Vérifier que l'asset existe
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # On va chercher suffisamment de points pour calculer tous les indicateurs
    max_window = max(window_short, window_long, 26, 50)

    prices = (
        db.query(Price)
        .filter(Price.asset_id == asset_id)
        .order_by(Price.timestamp.desc())
        .limit(max_window + 50)  # un peu de marge
        .all()
    )

    if not prices:
        raise HTTPException(status_code=404, detail="No price data for this asset")

    # Mettre dans l'ordre chronologique
    prices = list(reversed(prices))

    price_values = [p.price_usd for p in prices if p.price_usd is not None]
    if not price_values:
        current_price = None
    else:
        current_price = price_values[-1]

    # --- helpers internes ---
    def simple_moving_average(values, window: int):
        if window <= 0 or len(values) < window:
            return None
        subset = values[-window:]
        return sum(subset) / len(subset)

    def ema_series(values, window: int):
        if window <= 0 or len(values) < window:
            return []

        k = 2 / (window + 1)
        sma = sum(values[:window]) / window
        ema_vals = [sma]
        ema_prev = sma

        for price in values[window:]:
            ema_prev = price * k + ema_prev * (1 - k)
            ema_vals.append(ema_prev)

        return ema_vals

    def rsi(values, window: int = 14):
        if len(values) < window + 1:
            return None

        gains = []
        losses = []
        sliced = values[-(window + 1):]
        for i in range(1, len(sliced)):
            diff = sliced[i] - sliced[i - 1]
            if diff >= 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-diff)

        avg_gain = sum(gains) / window
        avg_loss = sum(losses) / window

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    # --- SMA ---
    ma_short = simple_moving_average(price_values, window_short)
    ma_long = simple_moving_average(price_values, window_long)

    # --- EMA + MACD ---
    ema_short_series = ema_series(price_values, 12)
    ema_long_series = ema_series(price_values, 26)

    ema_short_val = ema_short_series[-1] if ema_short_series else None
    ema_long_val = ema_long_series[-1] if ema_long_series else None

    macd_val = None
    macd_signal = None
    macd_hist = None

    if ema_short_series and ema_long_series:
        min_len = min(len(ema_short_series), len(ema_long_series))
        macd_series = [
            ema_short_series[-min_len + i] - ema_long_series[-min_len + i]
            for i in range(min_len)
        ]
        signal_series = ema_series(macd_series, 9)
        if macd_series and signal_series:
            macd_val = macd_series[-1]
            macd_signal = signal_series[-1]
            macd_hist = macd_val - macd_signal

    # --- RSI ---
    rsi_val = rsi(price_values, window=14)

    # --- Variation 24h depuis la dernière ligne Price ---
    change_24h_pct = prices[-1].change_24h_pct

    # --- Signal global ---
    signal = "neutral"
    if ma_short is not None and ma_long is not None:
        if ma_short > ma_long and (rsi_val is None or rsi_val < 70):
            signal = "bullish"
        elif ma_short < ma_long and (rsi_val is None or rsi_val > 30):
            signal = "bearish"

    return IndicatorOut(
        asset_id=asset_id,
        current_price=current_price,
        ma_short=ma_short,
        ma_long=ma_long,
        ema_short=ema_short_val,
        ema_long=ema_long_val,
        rsi=rsi_val,
        macd=macd_val,
        macd_signal=macd_signal,
        macd_hist=macd_hist,
        change_24h_pct=change_24h_pct,
        signal=signal,
    )



# --------------------------------------------------------------------
# INDICATORS (SMA/EMA/RSI/MACD)
# --------------------------------------------------------------------
# (❗ Je garde ton code indicateur tel qu’il était – PAS TOUCHÉ)


## =============================
# 📌 PORTFOLIO SYSTEM
# =============================
from sqlalchemy import func
from db import PortfolioTransaction, Price

@app.post("/portfolio/buy", response_model=TransactionOut)
def buy_crypto(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    asset = db.query(Asset).filter(Asset.id == tx.asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    latest_price = (
        db.query(Price)
        .filter(Price.asset_id == tx.asset_id)
        .order_by(Price.timestamp.desc())
        .first()
    )

    if not latest_price:
        raise HTTPException(400, "No price data for this asset")

    transaction = PortfolioTransaction(
        user_id=user.id,
        asset_id=tx.asset_id,
        quantity=tx.quantity,
        price_usd=latest_price.price_usd,
        is_buy=True,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@app.post("/portfolio/sell", response_model=TransactionOut)
def sell_crypto(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    asset = db.query(Asset).filter(Asset.id == tx.asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    total_bought = (
        db.query(func.sum(PortfolioTransaction.quantity))
        .filter_by(user_id=user.id, asset_id=tx.asset_id, is_buy=True)
        .scalar()
        or 0
    )

    total_sold = (
        db.query(func.sum(PortfolioTransaction.quantity))
        .filter_by(user_id=user.id, asset_id=tx.asset_id, is_buy=False)
        .scalar()
        or 0
    )

    available = total_bought - total_sold

    if tx.quantity > available:
        raise HTTPException(400, "Not enough balance to sell")

    latest_price = (
        db.query(Price)
        .filter(Price.asset_id == tx.asset_id)
        .order_by(Price.timestamp.desc())
        .first()
    )

    transaction = PortfolioTransaction(
        user_id=user.id,
        asset_id=tx.asset_id,
        quantity=tx.quantity,
        price_usd=latest_price.price_usd,
        is_buy=False,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@app.get("/portfolio/transactions", response_model=list[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    txs = (
        db.query(PortfolioTransaction)
        .filter(PortfolioTransaction.user_id == user.id)
        .order_by(PortfolioTransaction.timestamp.desc())
        .all()
    )
    return txs


@app.get("/portfolio/value")
def portfolio_value(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    txs = (
        db.query(PortfolioTransaction)
        .filter(PortfolioTransaction.user_id == user.id)
        .all()
    )

    if not txs:
        return {"value_usd": 0, "details": []}

    holdings = {}
    for tx in txs:
        holdings.setdefault(tx.asset_id, 0)
        holdings[tx.asset_id] += tx.quantity if tx.is_buy else -tx.quantity

    results = []
    total_value = 0

    for asset_id, qty in holdings.items():
        if qty <= 0:
            continue

        price = (
            db.query(Price)
            .filter(Price.asset_id == asset_id)
            .order_by(Price.timestamp.desc())
            .first()
        )

        if price:
            value = qty * price.price_usd
            total_value += value
            results.append({
                "asset_id": asset_id,
                "quantity": qty,
                "current_price": price.price_usd,
                "value_usd": value,
                "change_24h_pct": price.change_24h_pct,
            })

    return {"value_usd": total_value, "details": results}


# --------------------------------------------------------------------
# ALERTS
# --------------------------------------------------------------------
@app.post("/alerts", response_model=AlertOut)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    exists = db.query(Asset).filter(Asset.id == alert.asset_id).first()
    if not exists:
        raise HTTPException(404, "Asset not found")

    if alert.alert_type not in ["above", "below", "change_24h"]:
        raise HTTPException(400, "Invalid alert type")

    new_alert = Alert(
        user_id=user.id,
        asset_id=alert.asset_id,
        alert_type=alert.alert_type,
        target_value=alert.target_value,
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@app.get("/alerts", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return (
        db.query(Alert)
        .filter(Alert.user_id == user.id)
        .order_by(Alert.created_at.desc())
        .all()
    )


@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user.id).first()

    if not alert:
        raise HTTPException(404, "Alert not found")

    db.delete(alert)
    db.commit()
    return {"status": "deleted"}


# --------------------------------------------------------------------
# NOTIFICATIONS
# --------------------------------------------------------------------
@app.get("/notifications", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@app.post("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()

    if not notif:
        raise HTTPException(404, "Notification not found")

    notif.is_read = True
    db.commit()
    return {"status": "ok"}
