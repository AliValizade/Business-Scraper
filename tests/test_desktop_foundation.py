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
