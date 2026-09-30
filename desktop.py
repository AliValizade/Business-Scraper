from app.composition import create_application
from browser.manager import BrowserManager
from database.database import SessionLocal, init_db
from interfaces.desktop.app import run_desktop_app


def create_desktop_application():
    init_db()
    return create_application(
        session_factory=SessionLocal,
        browser_manager=BrowserManager(),
        source="google_maps",
    )


def main():
    application = create_desktop_application()
    return run_desktop_app(application=application)


if __name__ == "__main__":
    raise SystemExit(main())
