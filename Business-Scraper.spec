# PyInstaller specification for the Business-Scraper desktop application.

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("services") + collect_submodules("interfaces.desktop")

a = Analysis(
    ["desktop.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Business-Scraper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
