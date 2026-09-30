import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_source(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _imports(relative_path):
    tree = ast.parse(_read_source(relative_path))
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


def test_cli_depends_on_services_not_core():
    imports = _imports("cli/commands.py")

    assert "services.scrape_service" in imports
    assert "services.run_service" in imports
    assert "services.business_service" in imports
    assert "services.export_service" in imports
    assert not any(
        module and module.startswith("core")
        for module in imports
    )


def test_composition_root_is_the_service_wiring_location():
    imports = _imports("app/composition.py")

    assert "services.scrape_service" in imports
    assert "services.run_service" in imports
    assert "services.business_service" in imports
    assert "services.export_service" in imports


def test_service_modules_do_not_import_presentation_layers():
    for path in (
        "services/scrape_service.py",
        "services/run_service.py",
        "services/business_service.py",
        "services/export_service.py",
    ):
        imports = _imports(path)
        assert not any(
            module and (
                module == "cli"
                or module.startswith("cli.")
                or module == "gui"
                or module.startswith("gui.")
                or module == "api"
                or module.startswith("api.")
            )
            for module in imports
        )


def test_dto_module_does_not_import_application_or_presentation_layers():
    imports = _imports("services/dto.py")

    assert not any(
        module and (
            module == "app"
            or module.startswith("app.")
            or module == "cli"
            or module.startswith("cli.")
            or module == "gui"
            or module.startswith("gui.")
            or module == "api"
            or module.startswith("api.")
        )
        for module in imports
    )


def test_no_interface_cli_migration_is_required():
    assert (PROJECT_ROOT / "cli").is_dir()
    assert not (PROJECT_ROOT / "interfaces" / "cli").exists()
