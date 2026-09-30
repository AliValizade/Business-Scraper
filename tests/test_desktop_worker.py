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


def test_scrape_worker_supports_cooperative_cancellation():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "scrape_worker.py"
    ).read_text(encoding="utf-8")

    assert "cancelled = Signal()" in source
    assert "def cancel(self):" in source
    assert "_cancel_requested = True" in source


def test_desktop_ui_exposes_cancel_action():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert 'QPushButton("Cancel")' in source
    assert "def _cancel_scrape(self):" in source
    assert "self._scrape_worker.cancel()" in source
    assert "Scrape cancelled." in source
