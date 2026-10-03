# Business-Scraper Desktop Installer

## Build the desktop executable

From the repository root, install the Playwright Chromium browser into the Python environment so PyInstaller can bundle it:

### Git Bash

```bash
playwright install chromium
pyinstaller --clean --noconfirm Business-Scraper.spec
```

### PowerShell

```powershell
playwright install chromium
pyinstaller --clean --noconfirm Business-Scraper.spec
```

The expected executable is:

```
dist/Business-Scraper.exe
```

The PyInstaller spec collects the local `ms-playwright` browser directory and places it beside the frozen application payload. The frozen application then points Playwright to that bundled directory at startup.

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

## Source configuration

The desktop application uses Google Maps by default. To run the same executable with Neshan, configure the environment before launching it.

### Git Bash

```bash
export BUSINESS_SCRAPER_SOURCE=neshan
export NESHAN_API_KEY="your-api-key"
./dist/Business-Scraper.exe
```

### PowerShell

```powershell
$env:BUSINESS_SCRAPER_SOURCE = "neshan"
$env:NESHAN_API_KEY = "your-api-key"
.\\dist\\Business-Scraper.exe
```

If `BUSINESS_SCRAPER_SOURCE` is omitted, Google Maps remains the default. The API key is never stored in the repository or embedded in the executable.


Neshan desktop access is Web-first. `NESHAN_ACCESS_MODE=web` is the default and does not require an API key. The optional official API path can be selected with `NESHAN_ACCESS_MODE=api` and requires `NESHAN_API_KEY`.
