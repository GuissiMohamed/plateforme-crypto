import pytest
from collector import core
from collector import db as collector_db


def test_save_assets_inserts_asset_and_price(db_session):
    assets = [{
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 40000,
        "market_cap": 1,
        "total_volume": 2,
        "price_change_percentage_24h": 3.5,
    }]

    core.save_assets_to_db(assets)

    s = db_session
    a = s.get(collector_db.Asset, "bitcoin")
    assert a is not None
    assert a.symbol == "BTC"
    assert a.name == "Bitcoin"

    prices = s.query(collector_db.Price).filter_by(asset_id="bitcoin").all()
    assert len(prices) == 1
    assert prices[0].price_usd == 40000


def test_save_assets_does_not_duplicate_asset(db_session):
    assets = [{
        "id": "ethereum",
        "symbol": "eth",
        "name": "Ethereum",
        "current_price": 2000,
        "market_cap": 1,
        "total_volume": 2,
        "price_change_percentage_24h": 1.0,
    }]

    core.save_assets_to_db(assets)
    core.save_assets_to_db(assets)

    s = db_session
    assets_count = s.query(collector_db.Asset).filter_by(id="ethereum").count()
    prices_count = s.query(collector_db.Price).filter_by(asset_id="ethereum").count()

    assert assets_count == 1
    assert prices_count == 2


def test_save_assets_rollback_on_bad_payload(db_session):
    s = db_session
    assets_before = s.query(collector_db.Asset).count()
    prices_before = s.query(collector_db.Price).count()

    bad_assets = [{"symbol": "btc", "name": "Bitcoin"}]

    with pytest.raises(Exception):
        core.save_assets_to_db(bad_assets)

    assets_after = s.query(collector_db.Asset).count()
    prices_after = s.query(collector_db.Price).count()

    assert assets_after == assets_before
    assert prices_after == prices_before


def test_save_assets_allows_missing_optional_fields(db_session):
    assets = [{
        "id": "litecoin",
        "symbol": "ltc",
        "name": "Litecoin",
        # champs optionnels absents
    }]

    core.save_assets_to_db(assets)

    s = db_session
    a = s.get(collector_db.Asset, "litecoin")
    assert a is not None

    prices = s.query(collector_db.Price).filter_by(asset_id="litecoin").all()
    assert len(prices) == 1
    assert prices[0].price_usd is None


def test_price_is_linked_to_asset_relationship(db_session):
    assets = [{
        "id": "cardano",
        "symbol": "ada",
        "name": "Cardano",
        "current_price": 0.5,
        "market_cap": 1,
        "total_volume": 2,
        "price_change_percentage_24h": 0.1,
    }]
    core.save_assets_to_db(assets)

    s = db_session
    a = s.get(collector_db.Asset, "cardano")
    assert a is not None
    assert len(a.prices) >= 1
    assert a.prices[-1].asset_id == "cardano"
