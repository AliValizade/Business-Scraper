from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_desktop_gui_exposes_source_selection():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "self.source_combo = QComboBox()" in source
    assert 'self.source_combo.addItem("Google Maps", "google_maps")' in source
    assert 'self.source_combo.addItem("Neshan", "neshan")' in source


def test_desktop_gui_exposes_access_mode_selection():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "self.access_mode_combo = QComboBox()" in source
    assert 'self.access_mode_combo.addItem("Web", "web")' in source
    assert 'self.access_mode_combo.addItem("API", "api")' in source


def test_desktop_api_key_is_only_enabled_for_api_mode():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "self.api_key_input.setEnabled(is_api)" in source
    assert "api_key=api_key" in source


def test_desktop_scrape_request_contains_source_and_access_mode():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "source=source" in source
    assert "access_mode=access_mode" in source


def test_desktop_google_maps_api_key_is_available():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert 'self.api_key_input.setPlaceholderText("Google Maps API key")' in source
