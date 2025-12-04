# backend/main.py

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func


from db import SessionLocal, init_db, Asset, Price, User
from schemas import AssetOut, PriceOut, IndicatorOut, UserOut, Token, UserCreate
from auth import (
    
    get_current_active_user,
    get_current_admin,
    get_password_hash,
    authenticate_user,
    create_access_token,
)

from db import SessionLocal, init_db, Asset, Price, User, PortfolioTransaction
from schemas import (
    AssetOut,
    PriceOut,
    IndicatorOut,
    UserOut,
    Token,
    UserCreate,
    TransactionCreate,
    TransactionOut,
)

from auth import (
    get_current_active_user,
    get_current_admin,
    get_password_hash,
    authenticate_user,
    create_access_token,
)


app = FastAPI(
    title="Crypto Market Analytics API",
    version="0.1.0",
    description="API backend pour la plateforme de surveillance et d'analyse des marchés de cryptomonnaies.",
)

# Middleware CORS pour que le frontend (React) puisse appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # plus tard, tu pourras restreindre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """
    Dépendance FastAPI pour obtenir une session de base de données.
    Elle sera automatiquement fermée après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    """
    Hook exécuté au démarrage de l'application.
    On s'assure que la base est initialisée.
    """
    init_db()


@app.get("/health")
def health():
    """
    Endpoint de santé simple pour vérifier que l'API fonctionne.
    """
    return {"status": "ok"}

@app.post("/auth/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash sécurisé
    raw_password = user_in.password.strip()[:72]   # <-- IMPORTANT !
    hashed = get_password_hash(raw_password)

    # Créer user
    user = User(
        email=user_in.email,
        hashed_password=hashed,
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authentifie un utilisateur et renvoie un token JWT.
    Le client doit envoyer les champs 'username' (email) et 'password'.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Renvoie les informations de l'utilisateur courant (protégé par JWT).
    """
    return current_user



@app.get("/assets", response_model=List[AssetOut])
def list_assets(limit: int = 100, db: Session = Depends(get_db)):
    """
    Renvoie la liste des cryptomonnaies connues (table assets).
    On limite le nombre de résultats avec 'limit'.
    """
    assets = (
        db.query(Asset)
        .order_by(Asset.symbol.asc())
        .limit(limit)
        .all()
    )
    return assets




# ... ici ton code existant (app, middleware, get_db, /health, /assets)

@app.get("/assets/{asset_id}/prices", response_model=List[PriceOut])
def get_asset_prices(
    asset_id: str,
    limit: int = 100,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Renvoie l'historique des prix pour une crypto donnée.

    - `limit` : nombre max de points (par défaut 100)
    - `start` : (optionnel) date de début (ISO 8601)
    - `end`   : (optionnel) date de fin (ISO 8601)
    """

    # Vérifier que l'asset existe
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    query = db.query(Price).filter(Price.asset_id == asset_id)

    # Filtres temporels
    if start is not None:
        query = query.filter(Price.timestamp >= start)
    if end is not None:
        query = query.filter(Price.timestamp <= end)

    # On trie du plus récent au plus ancien, puis on limite
    query = query.order_by(Price.timestamp.desc()).limit(limit)

    prices = query.all()

    if not prices:
        raise HTTPException(status_code=404, detail="No price data for this asset in given range")

    # On inverse la liste pour renvoyer du plus ancien au plus récent (pratique pour les graphes)
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
    - ema_short / ema_long : moyennes mobiles exponentielles (12/26 par défaut)
    - rsi : Relative Strength Index (14 périodes)
    - macd, macd_signal, macd_hist : MACD 12/26/9
    - change_24h_pct : variation 24h (depuis la dernière ligne Price)
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
        .limit(max_window + 50)  # on prend un peu plus pour MACD/RSI
        .all()
    )

    if not prices:
        raise HTTPException(status_code=404, detail="No price data for this asset")

    # On remet dans l'ordre chronologique (du plus ancien au plus récent)
    prices = list(reversed(prices))

    # Liste des prix
    price_values = [p.price_usd for p in prices if p.price_usd is not None]

    if not price_values:
        current_price = None
    else:
        current_price = price_values[-1]  # dernier prix

    def simple_moving_average(values, window: int):
        """Moyenne mobile simple."""
        if window <= 0 or len(values) < window:
            return None
        subset = values[-window:]
        return sum(subset) / len(subset)

    def ema_series(values, window: int):
        """Renvoie la série complète d'EMA pour un window donné."""
        if window <= 0 or len(values) < window:
            return []

        k = 2 / (window + 1)
        # On initialise l'EMA avec la SMA des 'window' premiers points
        sma = sum(values[:window]) / window
        ema_vals = [sma]
        ema_prev = sma

        for price in values[window:]:
            ema_prev = price * k + ema_prev * (1 - k)
            ema_vals.append(ema_prev)

        return ema_vals

    def rsi(values, window: int = 14):
        """Calcule un RSI basique sur les 'window' dernières variations."""
        if len(values) < window + 1:
            return None

        gains = []
        losses = []
        # On ne regarde que les 'window' dernières variations
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

    # -------------------------
    # SMA
    # -------------------------
    ma_short = simple_moving_average(price_values, window_short)
    ma_long = simple_moving_average(price_values, window_long)

    # -------------------------
    # EMA + MACD
    # -------------------------
    ema_short_series = ema_series(price_values, 12)
    ema_long_series = ema_series(price_values, 26)

    ema_short_val = ema_short_series[-1] if ema_short_series else None
    ema_long_val = ema_long_series[-1] if ema_long_series else None

    macd_val = None
    macd_signal = None
    macd_hist = None

    if ema_short_series and ema_long_series:
        # On aligne les séries sur la longueur de la plus longue
        # EMA26 commence plus tard → on se base sur sa longueur
        min_len = min(len(ema_short_series), len(ema_long_series))
        macd_series = [
            ema_short_series[-min_len + i] - ema_long_series[-min_len + i]
            for i in range(min_len)
        ]

        # Signal = EMA 9 périodes sur la série MACD
        signal_series = ema_series(macd_series, 9)
        if macd_series and signal_series:
            macd_val = macd_series[-1]
            macd_signal = signal_series[-1]
            macd_hist = macd_val - macd_signal

    # -------------------------
    # RSI
    # -------------------------
    rsi_val = rsi(price_values, window=14)

    # -------------------------
    # Variation 24h
    # -------------------------
    change_24h_pct = prices[-1].change_24h_pct

    # -------------------------
    # Signal global
    # -------------------------
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


@app.post("/portfolio/sell", response_model=TransactionOut)
def sell_crypto(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    # Vérifier l'existence de la crypto
    asset = db.query(Asset).filter(Asset.id == tx.asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    # Vérifier que l'utilisateur a assez de crypto pour vendre
    total_bought = (
        db.query(PortfolioTransaction)
        .filter_by(user_id=user.id, asset_id=tx.asset_id, is_buy=True)
        .with_entities(func.sum(PortfolioTransaction.quantity))
        .scalar()
        or 0
    )

    total_sold = (
        db.query(PortfolioTransaction)
        .filter_by(user_id=user.id, asset_id=tx.asset_id, is_buy=False)
        .with_entities(func.sum(PortfolioTransaction.quantity))
        .scalar()
        or 0
    )

    available = total_bought - total_sold

    if tx.quantity > available:
        raise HTTPException(400, "Not enough balance to sell")

    # Prix actuel
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

    # Regrouper les quantités nettes par crypto
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
            })

    return {"value_usd": total_value, "details": results}
