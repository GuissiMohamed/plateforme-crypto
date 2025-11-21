# collector/db.py

from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# URL de connexion à la base PostgreSQL
# Elle correspond aux paramètres du docker run
DATABASE_URL = "postgresql+psycopg2://crypto_user:crypto_pass@localhost:5432/cryptodb"

# Création du moteur de connexion
engine = create_engine(DATABASE_URL, echo=False)

# Fabrique de sessions (pour parler à la base)
SessionLocal = sessionmaker(bind=engine)

# Classe de base pour les modèles
Base = declarative_base()


class Asset(Base):
    """
    Représente une cryptomonnaie (Bitcoin, Ethereum, etc.)
    """
    __tablename__ = "assets"

    # exemple d'id dans CoinCap : "bitcoin", "ethereum"
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)  # BTC, ETH...
    name = Column(String)

    prices = relationship("Price", back_populates="asset")


class Price(Base):
    """
    Représente un point de prix pour une crypto à un instant donné.
    """
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    price_usd = Column(Float)
    market_cap_usd = Column(Float)
    volume_24h_usd = Column(Float)
    change_24h_pct = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="prices")


def init_db():
    """
    Crée les tables dans la base si elles n'existent pas encore.
    """
    Base.metadata.create_all(bind=engine)
