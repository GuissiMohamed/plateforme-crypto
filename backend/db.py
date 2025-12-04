# backend/db.py

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

# ⚠️ Même URL que dans collector/db.py
DATABASE_URL = "postgresql+psycopg2://crypto_user:crypto_pass@localhost:5432/cryptodb"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)

    prices = relationship("Price", back_populates="asset")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    price_usd = Column(Float)
    market_cap_usd = Column(Float)
    volume_24h_usd = Column(Float)
    change_24h_pct = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="prices")


from sqlalchemy import Boolean  # ajoute cet import en haut si pas présent
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # "user" ou "admin"


class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(String, ForeignKey("assets.id"))

    quantity = Column(Float, nullable=False)  # quantité de crypto achetée/vendue
    price_usd = Column(Float, nullable=False) # prix au moment de la transaction

    is_buy = Column(Boolean, nullable=False)  # True = achat, False = vente
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    asset = relationship("Asset")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)

    # Type d'alerte : "above", "below", "change_24h"
    alert_type = Column(String, nullable=False)

    # Valeur ciblée (ex: BTC > 50000, ADA < 0.40, etc.)
    target_value = Column(Float, nullable=False)

    # L'alerte peut être déclenchée une seule fois
    triggered = Column(Boolean, default=False)

    # Pour historique
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)

    # Relations ORM (pas obligatoire mais propre)
    user = relationship("User")
    asset = relationship("Asset")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ⭐ CHAMP MANQUANT AJOUTÉ
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)

    message = Column(String, nullable=False)

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    asset = relationship("Asset")


# Utilisé par auth.py pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def init_db():
    """
    Crée les tables si elles n'existent pas.
    Normalement elles existent déjà grâce au collector, donc c'est safe.
    """
    Base.metadata.create_all(bind=engine)
