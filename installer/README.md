# Business-Scraper Desktop Installer

## Build the desktop executable

From the repository root, install the Playwright Chromium browser into the Python environment so PyInstaller can bundle it:

### Git Bash

```bash
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium
pyinstaller --clean --noconfirm Business-Scraper.spec
```

### PowerShell

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
playwright install chromium
pyinstaller --clean --noconfirm Business-Scraper.spec
```

The expected executable is:

```
dist/Business-Scraper.exe
```

The bundled Chromium makes the desktop executable self-contained for Playwright browser execution. Playwright documents this PyInstaller approach officially.

## Build the Inno Setup installer

Open:

```
installer/Business-Scraper.iss
```

in Inno Setup and compile it.

The installer expects the one-file executable at:

```
dist/Business-Scraper.exe
```

and produces the installer under:

```
dist/installer/
```

## First run

On first launch, the application initializes the SQLite schema automatically.

The current database location remains under the application's database directory. Moving user data to an OS-specific user-data directory is intentionally deferred to avoid an unnecessary infrastructure refactor.

## User data

Uninstalling the application does not explicitly delete user-created database or export data.
