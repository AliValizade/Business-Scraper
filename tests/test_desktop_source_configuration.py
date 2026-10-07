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



def test_desktop_google_maps_api_key_placeholder_is_source_aware():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert '"Google Maps API key"' in source
    assert '"Neshan API key"' in source
    assert '"API key"' in source


def _desktop_source():
    return (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")


def test_desktop_source_and_mode_preferences_are_persisted():
    source = _desktop_source()
    assert 'self.settings.value("source", "google_maps")' in source
    assert 'self.settings.value("access_mode", "web")' in source
    assert 'self.settings.setValue("source", self.source_combo.currentData())' in source
    assert 'self.settings.setValue("access_mode", self.access_mode_combo.currentData())' in source


def test_desktop_api_key_is_hidden_outside_api_mode():
    source = _desktop_source()
    assert "self.api_key_input.setVisible(is_api)" in source


def test_desktop_ui_has_modern_window_basics():
    source = _desktop_source()
    assert 'self.setMinimumSize(1050, 720)' in source
    assert 'border-radius: 12px' in source
    assert 'font-size: 22pt' in source


def test_desktop_scrape_form_uses_compact_grid_layout():
    source = _desktop_source()
    assert "form = QGridLayout(scrape_group)" in source
    assert "self.api_key_label.setVisible(is_api)" in source
    assert "self.runs_table.setMinimumHeight(145)" in source
    assert "self.businesses_table.setMinimumHeight(145)" in source
