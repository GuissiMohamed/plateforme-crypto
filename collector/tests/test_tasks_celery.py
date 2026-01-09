from collector import tasks


def test_collect_market_data_calls_init_and_collect(monkeypatch):
    called = {"init_db": 0, "collect_once": 0}

    def fake_init_db():
        called["init_db"] += 1

    def fake_collect_once():
        called["collect_once"] += 1

    monkeypatch.setattr(tasks, "init_db", fake_init_db)
    monkeypatch.setattr(tasks, "collect_once", fake_collect_once)

    tasks.collect_market_data()

    assert called["init_db"] == 1
    assert called["collect_once"] == 1


def test_setup_periodic_tasks_registers_job():
    class DummySender:
        def __init__(self):
            self.calls = []

        def add_periodic_task(self, schedule, sig, name=None):
            self.calls.append((schedule, sig, name))

    sender = DummySender()
    tasks.setup_periodic_tasks(sender)

    assert len(sender.calls) == 1
    schedule, sig, name = sender.calls[0]
    assert schedule == 300.0
    assert "Collecte" in (name or "")
