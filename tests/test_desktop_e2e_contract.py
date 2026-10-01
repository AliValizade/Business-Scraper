from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_desktop_e2e_entrypoint_contract():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert "configure_playwright_browsers_path()" in source
    assert "init_db()" in source
    assert "create_application(" in source
    assert "run_desktop_app(application=application)" in source


def test_desktop_e2e_persistent_license_is_composed():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert "QSettingsLicenseStateStore()" in source
    assert "LicenseService(store=QSettingsLicenseStateStore())" in source


def test_desktop_e2e_playwright_bundle_contract():
    spec = (PROJECT_ROOT / "Business-Scraper.spec").read_text(encoding="utf-8")

    assert '"ms-playwright"' in spec
    assert 'datas=datas' in spec
    assert 'name="Business-Scraper"' in spec


def test_desktop_e2e_installer_consumes_onefile_executable():
    iss = (
        PROJECT_ROOT / "installer" / "Business-Scraper.iss"
    ).read_text(encoding="utf-8")

    assert 'Source: "..\\dist\\Business-Scraper.exe"' in iss
    assert 'Filename: "{app}\\{#MyAppExeName}"' in iss


def test_desktop_e2e_installer_and_packaging_docs_match():
    readme = (
        PROJECT_ROOT / "installer" / "README.md"
    ).read_text(encoding="utf-8")

    assert "dist/Business-Scraper.exe" in readme
    assert "ms-playwright" in readme
    assert "playwright install chromium" in readme
    assert "Inno Setup" in readme


def test_desktop_e2e_database_is_initialized_before_application_start():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    init_index = source.index("init_db()")
    compose_index = source.index("create_application(")

    assert init_index < compose_index


def test_desktop_e2e_ui_supports_scrape_export_and_second_run():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert 'QPushButton("Start Scrape")' in source
    assert 'QPushButton("Export Selected Run")' in source
    assert "self._restore_scrape_controls()" in source
    assert "self.application.export_run(" in source


def test_desktop_e2e_close_blocks_while_scrape_is_running():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "if self._scrape_thread is not None and self._scrape_thread.isRunning():" in source
    assert 'event.ignore()' in source
