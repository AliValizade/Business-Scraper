import os
import sys
from pathlib import Path

from app.composition import create_application
from browser.manager import BrowserManager
from database.database import SessionLocal, init_db
from interfaces.desktop.app import run_desktop_app
from interfaces.desktop.license_store import QSettingsLicenseStateStore


def configure_playwright_browsers_path() -> None:
    """Point frozen applications at the bundled Playwright browsers."""
    if not getattr(sys, "frozen", False):
        return

    base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    browsers = base / "ms-playwright"
    if browsers.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers)


def create_desktop_application():
    configure_playwright_browsers_path()
    init_db()
    return create_application(
        session_factory=SessionLocal,
        browser_manager=BrowserManager(),
        source="google_maps",
        license_service=None,
    )


def main():
    application = create_desktop_application()
    return run_desktop_app(application=application)


if __name__ == "__main__":
    raise SystemExit(main())
