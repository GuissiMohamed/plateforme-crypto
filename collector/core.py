# collector/core.py

import requests
from datetime import datetime

from db import SessionLocal, Asset, Price

API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"


def fetch_assets():
    """
    Appelle l'API CoinGecko et renvoie la liste des cryptomonnaies.
    """
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data  # CoinGecko renvoie directement une liste


def save_assets_to_db(assets_data):
    """
    Sauvegarde les cryptos et leurs prix dans la base de données.
    """
    session = SessionLocal()

    try:
        for item in assets_data:
            asset_id = item["id"]              # ex: "bitcoin"
            symbol = item["symbol"].upper()    # ex: "BTC"
            name = item["name"]                # ex: "Bitcoin"

            price_usd = item.get("current_price")
            market_cap_usd = item.get("market_cap")
            volume_24h_usd = item.get("total_volume")
            change_24h_pct = item.get("price_change_percentage_24h")

            asset = session.get(Asset, asset_id)
            if asset is None:
                asset = Asset(
                    id=asset_id,
                    symbol=symbol,
                    name=name,
                )
                session.add(asset)

            price = Price(
                asset_id=asset_id,
                price_usd=price_usd,
                market_cap_usd=market_cap_usd,
                volume_24h_usd=volume_24h_usd,
                change_24h_pct=change_24h_pct,
                timestamp=datetime.utcnow(),
            )
            session.add(price)

        session.commit()
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'enregistrement en base :", e)
        raise
    finally:
        session.close()


def collect_once():
    """
    Effectue une collecte complète : API -> base.
    """
    print(f"[{datetime.utcnow()}] Début de la collecte…")
    assets = fetch_assets()
    print(f"[{datetime.utcnow()}] {len(assets)} cryptomonnaies récupérées, enregistrement…")
    save_assets_to_db(assets)
    print(f"[{datetime.utcnow()}] Collecte terminée ✅")
