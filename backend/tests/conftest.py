import os
import pytest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

import db as db_module
import auth as auth_module
import main as main_module


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    # SQLite fichier (évite les soucis du :memory: avec multiples connexions)
    db_file = tmp_path_factory.mktemp("data") / "test.sqlite"
    engine = create_engine(
        f"sqlite+pysqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    return engine


@pytest.fixture(scope="session")
def TestingSessionLocal(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def patch_db(test_engine, TestingSessionLocal):
    """
    Patch le module db (engine + SessionLocal) AVANT que l'app démarre.
    """
    db_module.engine = test_engine
    db_module.SessionLocal = TestingSessionLocal

    # Recrée toutes les tables
    db_module.Base.metadata.drop_all(bind=test_engine)
    db_module.Base.metadata.create_all(bind=test_engine)


@pytest.fixture()
def db_session(TestingSessionLocal):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """
    Override main.get_db ET db.get_db (utilisé par auth.py)
    pour garantir une SEULE session SQLAlchemy dans toute la requête.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # endpoints (main.py)
    main_module.app.dependency_overrides[main_module.get_db] = override_get_db
    # auth.py dépend de db.get_db (importé dans auth.py)
    main_module.app.dependency_overrides[db_module.get_db] = override_get_db

    with TestClient(main_module.app) as c:
        yield c

    main_module.app.dependency_overrides.clear()



@pytest.fixture()
def seed_user(db_session):
    # crée un user en DB
    email = "test@example.com"
    password = "Password123!"

    user = db_session.query(db_module.User).filter_by(email=email).first()
    if not user:
        user = db_module.User(
            email=email,
            hashed_password=auth_module.get_password_hash(password),
            is_active=True,
            role="user",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return {"email": email, "password": password, "user": user}


@pytest.fixture()
def auth_headers(client, seed_user):
    # login via endpoint pour récupérer un token
    r = client.post(
        "/auth/login",
        data={"username": seed_user["email"], "password": seed_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def seed_asset_prices(db_session):
    # asset
    asset = db_session.query(db_module.Asset).filter_by(id="bitcoin").first()
    if not asset:
        asset = db_module.Asset(id="bitcoin", symbol="BTC", name="Bitcoin")
        db_session.add(asset)
        db_session.commit()

    # prices : on met suffisamment de points pour indicators (SMA/EMA/RSI/MACD)
    existing = db_session.query(db_module.Price).filter_by(asset_id="bitcoin").count()
    if existing < 120:
        # purge ancien pour éviter doublons timestamp
        db_session.query(db_module.Price).filter_by(asset_id="bitcoin").delete()
        db_session.commit()

        base_time = datetime.utcnow() - timedelta(minutes=120)
        price = 40000.0
        for i in range(120):
            price += 10.0  # tendance légère haussière
            p = db_module.Price(
                asset_id="bitcoin",
                price_usd=price,
                market_cap_usd=1.0,
                volume_24h_usd=1.0,
                change_24h_pct=2.5,
                timestamp=base_time + timedelta(minutes=i),
            )
            db_session.add(p)

        db_session.commit()

    return {"asset_id": "bitcoin"}
