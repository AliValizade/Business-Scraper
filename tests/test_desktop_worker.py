from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_scrape_worker_exists_and_uses_service_boundary():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "scrape_worker.py"
    ).read_text(encoding="utf-8")

    assert "ScrapeWorker" in source
    assert "QThread" not in source
    assert "start_scrape" in source
    assert "finished = Signal(object)" in source
    assert "failed = Signal(str)" in source
