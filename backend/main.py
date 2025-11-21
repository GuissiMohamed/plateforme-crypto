# backend/main.py

from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import SessionLocal, init_db, Asset, Price
from schemas import AssetOut, PriceOut, IndicatorOut

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
    Renvoie quelques indicateurs techniques simples pour une cryptomonnaie :

    - current_price : dernier prix connu
    - ma_short      : moyenne mobile sur 'window_short' derniers points
    - ma_long       : moyenne mobile sur 'window_long' derniers points
    - change_24h_pct: variation sur 24h (depuis la dernière ligne Price)
    - signal        : "bullish" si ma_short > ma_long,
                      "bearish" si ma_short < ma_long,
                      "neutral" sinon.
    """

    # Vérifier que l'asset existe
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # On va chercher suffisamment de points pour calculer les moyennes
    max_window = max(window_short, window_long)

    prices = (
        db.query(Price)
        .filter(Price.asset_id == asset_id)
        .order_by(Price.timestamp.desc())
        .limit(max_window)
        .all()
    )

    if not prices:
        raise HTTPException(status_code=404, detail="No price data for this asset")

    # On remet dans l'ordre chronologique (du plus ancien au plus récent)
    prices = list(reversed(prices))

    # On récupère juste les valeurs de prix (en filtrant les None au cas où)
    price_values = [p.price_usd for p in prices if p.price_usd is not None]

    if not price_values:
        current_price = None
    else:
        current_price = price_values[-1]  # dernier prix

    def simple_moving_average(values, window: int):
        """
        Calcule la moyenne mobile simple sur les 'window' derniers points.
        Renvoie None si on n'a pas assez de données.
        """
        if window <= 0 or len(values) < window:
            return None
        subset = values[-window:]
        return sum(subset) / len(subset)

    ma_short = simple_moving_average(price_values, window_short)
    ma_long = simple_moving_average(price_values, window_long)

    # Variation 24h : on prend la dernière valeur disponible
    change_24h_pct = prices[-1].change_24h_pct

    # Petit "signal" basique
    signal = None
    if ma_short is not None and ma_long is not None:
        if ma_short > ma_long:
            signal = "bullish"
        elif ma_short < ma_long:
            signal = "bearish"
        else:
            signal = "neutral"

    return IndicatorOut(
        asset_id=asset_id,
        current_price=current_price,
        ma_short=ma_short,
        ma_long=ma_long,
        change_24h_pct=change_24h_pct,
        signal=signal,
    )
