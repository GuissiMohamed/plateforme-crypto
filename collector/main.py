# collector/main.py

import requests
from datetime import datetime

from db import SessionLocal, init_db, Asset, Price

API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"


def fetch_assets():
    """
    Appelle l'API CoinGecko et renvoie la liste des cryptomonnaies.
    """
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data  # CoinGecko renvoie directement une liste de cryptos


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

            # Prix et autres infos (déjà en float avec CoinGecko)
            price_usd = item.get("current_price")
            market_cap_usd = item.get("market_cap")
            volume_24h_usd = item.get("total_volume")
            change_24h_pct = item.get("price_change_percentage_24h")

            # Vérifier si l'asset existe déjà
            asset = session.get(Asset, asset_id)
            if asset is None:
                asset = Asset(
                    id=asset_id,
                    symbol=symbol,
                    name=name,
                )
                session.add(asset)

            # Historique des prix
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


def main():
    print("Initialisation de la base de données…")
    init_db()

    print("Récupération des données depuis CoinGecko…")
    assets = fetch_assets()
    print(f"{len(assets)} cryptomonnaies récupérées.")

    print("Enregistrement en base de données…")
    save_assets_to_db(assets)

    print("Terminé ✅")


if __name__ == "__main__":
    main()
