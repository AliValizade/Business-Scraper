import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _imports(relative_path):
    tree = ast.parse(
        (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
    )
    return {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }


def test_desktop_entrypoint_isolated_from_core_and_scrapers():
    imports = _imports("interfaces/desktop/main_window.py")
    assert not any(
        module and (
            module.startswith("core")
            or module.startswith("scrapers")
            or module.startswith("database")
        )
        for module in imports
    )


def test_desktop_app_depends_on_desktop_presentation_only():
    imports = _imports("interfaces/desktop/app.py")
    assert "interfaces.desktop.main_window" in imports
    assert not any(
        module and module.startswith("core")
        for module in imports
    )


def test_desktop_foundation_files_exist():
    assert (PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py").is_file()
    assert (PROJECT_ROOT / "interfaces" / "desktop" / "app.py").is_file()
    assert (PROJECT_ROOT / "desktop.py").is_file()


def test_desktop_dependency_is_declared():
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(
        encoding="utf-8"
    )
    assert "PySide6" in requirements


def test_desktop_scrape_ui_exposes_expected_controls():
    source = (PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py").read_text(
        encoding="utf-8"
    )

    for name in (
        "location_input",
        "keywords_input",
        "max_results_input",
        "scrape_button",
        "status_label",
        "result_label",
    ):
        assert name in source


def test_desktop_scrape_ui_uses_service_dto_boundary():
    source = (PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py").read_text(
        encoding="utf-8"
    )

    assert "ScrapeRequestDTO.from_values" in source
    assert "ScrapeWorker(" in source
    assert "self.application.scrape_service" in source


def test_desktop_runs_and_business_inspection_ui_exists():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    for name in (
        "runs_table",
        "businesses_table",
        "refresh_runs_button",
        "_load_runs",
        "_load_selected_run_businesses",
        "run_service.list_runs",
        "run_service.get_run_businesses",
    ):
        assert name in source


def test_desktop_inspection_uses_run_service_boundary():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "self.application.run_service" in source
    assert "core.models" not in source


def test_desktop_export_ui_exists():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    for name in (
        "export_format_combo",
        "export_button",
        "_export_selected_run",
        "QFileDialog.getSaveFileName",
        "application.export_service.export_run",
    ):
        assert name in source


def test_desktop_export_supports_expected_formats():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert '"csv"' in source
    assert '"excel"' in source
    assert '"json"' in source
    assert "ExportResultDTO" not in source


def test_desktop_settings_and_error_ux_exists():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "QSettings" in source
    assert '"window_size"' in source
    assert '"export_format"' in source
    assert "def closeEvent" in source
    assert "def _set_status" in source
    assert "error=True" in source


def test_desktop_settings_are_presentation_only():
    source = (
        PROJECT_ROOT / "interfaces" / "desktop" / "main_window.py"
    ).read_text(encoding="utf-8")

    assert "config.py" not in source
    assert "core.models" not in source



def test_desktop_entrypoint_composes_real_application():
    source = (PROJECT_ROOT / "desktop.py").read_text(encoding="utf-8")

    assert "create_application" in source
    assert "SessionLocal" in source
    assert "BrowserManager" in source
    assert "run_desktop_app(application=application)" in source


def test_pyinstaller_spec_exists_and_targets_desktop_entrypoint():
    spec = (PROJECT_ROOT / "Business-Scraper.spec").read_text(encoding="utf-8")

    assert '"desktop.py"' in spec
    assert 'name="Business-Scraper"' in spec
    assert "collect_submodules" in spec



def test_inno_setup_installer_definition_exists():
    iss = (PROJECT_ROOT / "installer" / "Business-Scraper.iss").read_text(
        encoding="utf-8"
    )

    assert 'AppName={#MyAppName}' in iss
    assert 'DefaultDirName={autopf}\\Business-Scraper' in iss
    assert 'Source: "dist\\Business-Scraper\\*"' in iss
    assert 'Filename: "{app}\\{#MyAppExeName}"' in iss


def test_desktop_installer_documents_build_and_first_run():
    readme = (PROJECT_ROOT / "installer" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "pyinstaller --clean --noconfirm Business-Scraper.spec" in readme
    assert "dist/Business-Scraper/" in readme
    assert "initializes the SQLite schema" in readme
