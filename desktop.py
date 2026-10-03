import os
import sys
from pathlib import Path

from app.composition import create_application
from browser.manager import BrowserManager
from database.database import SessionLocal, init_db
from interfaces.desktop.app import run_desktop_app
from interfaces.desktop.license_store import QSettingsLicenseStateStore
from services.license_service import LicenseService


def configure_playwright_browsers_path() -> None:
    """Point frozen applications at the bundled Playwright browsers."""
    if not getattr(sys, "frozen", False):
        return

    base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    browsers = base / "ms-playwright"
    if browsers.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers)


def get_desktop_source() -> str:
    """Read the desktop source from configuration."""
    return os.getenv(
        "BUSINESS_SCRAPER_SOURCE",
        "google_maps",
    ).strip().lower()


def get_desktop_scraper_kwargs(source: str) -> dict:
    """Build source-specific desktop scraper configuration."""
    if source == "neshan":
        return {
            "api_key": os.getenv("NESHAN_API_KEY"),
        }

    return {}


def create_desktop_application():
    configure_playwright_browsers_path()
    init_db()

    return create_application(
        session_factory=SessionLocal,
        browser_manager=BrowserManager(),
        license_service=LicenseService(
            store=QSettingsLicenseStateStore()
        ),
    )


def main():
    application = create_desktop_application()
    return run_desktop_app(application=application)


if __name__ == "__main__":
    raise SystemExit(main())
