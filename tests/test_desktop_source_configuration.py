from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_desktop_source_defaults_to_google_maps():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert "BUSINESS_SCRAPER_SOURCE" in source
    assert '"google_maps"' in source
    assert "get_desktop_source" in source


def test_desktop_source_supports_neshan():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert 'if source == "neshan":' in source
    assert '"api_key": os.getenv("NESHAN_API_KEY")' in source
    assert '"mode": os.getenv("NESHAN_ACCESS_MODE", "web")' in source


def test_desktop_passes_configured_source_to_application():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert "source=source" in source
    assert "scraper_kwargs=get_desktop_scraper_kwargs(source)" in source
