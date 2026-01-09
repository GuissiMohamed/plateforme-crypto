import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from collector import db as collector_db
from collector import core as core_module



@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "collector_test.sqlite"
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
def patch_collector_db(test_engine, TestingSessionLocal):
    collector_db.engine = test_engine
    collector_db.SessionLocal = TestingSessionLocal

    # core.py a importé SessionLocal/Asset/Price depuis db, donc on patch aussi
    core_module.SessionLocal = TestingSessionLocal
    core_module.Asset = collector_db.Asset
    core_module.Price = collector_db.Price

    collector_db.Base.metadata.drop_all(bind=test_engine)
    collector_db.Base.metadata.create_all(bind=test_engine)


@pytest.fixture()
def db_session(TestingSessionLocal):
    s = TestingSessionLocal()
    try:
        yield s
    finally:
        s.close()
