from pathlib import Path


def _desktop_source():
    return (PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py").read_text(encoding="utf-8")



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


def test_desktop_dashboard_has_collapsible_sidebar_navigation():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert 'self.sidebar = QWidget()' in source
    assert 'self.sidebar_menu.addItems(["Dashboard", "Scrape", "Runs", "Results", "Settings", "License"])' in source
    assert 'self.menu_button = QPushButton("☰")' in source
    assert 'self.sidebar.setFixedWidth(62 if self.sidebar_collapsed else 210)' in source


def test_desktop_dashboard_uses_stacked_pages():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "self.pages = QStackedWidget()" in source
    assert "self._build_dashboard_page()" in source
    assert "self._build_scrape_page()" in source
    assert "self._build_runs_page()" in source
    assert "self._build_results_page()" in source
    assert "self._build_settings_page()" in source
    assert "self._build_license_page()" in source
    assert "self.resize(1000, 700)" in source


def test_desktop_supports_light_and_dark_themes():
    source = _desktop_source()
    assert 'self.dark_mode = str(self.settings.value("theme", "light")).lower() == "dark"' in source
    assert 'self.settings.setValue("theme", "dark" if self.dark_mode else "light")' in source
    assert "QWidget#Sidebar" in source
    assert "Switch to Dark" in source
    assert "Switch to Light" in source


def test_desktop_progress_bar_is_readable():
    source = _desktop_source()
    assert "self.progress_bar.setMinimumHeight(18)" in source
    assert "text-align: center" in source


def test_run_rows_open_results_directly():
    source = _desktop_source()
    assert "self.runs_table.cellClicked.connect(self._open_run_results)" in source
    assert "self.sidebar_menu.setCurrentRow(3)" in source
