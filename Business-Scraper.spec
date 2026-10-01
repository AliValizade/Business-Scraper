# PyInstaller specification for the Business-Scraper desktop application.

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


playwright_browsers = (
    Path(os.environ["USERPROFILE"])
    / "AppData"
    / "Local"
    / "ms-playwright"
)

datas = []
if playwright_browsers.exists():
    datas.append((str(playwright_browsers), "ms-playwright"))

hiddenimports = collect_submodules("services") + collect_submodules("interfaces.desktop")

a = Analysis(
    ["desktop.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
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
