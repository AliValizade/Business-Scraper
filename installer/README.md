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

## Source and access mode

Source and access mode are selected directly in the Desktop GUI.

Available source selections currently include:

- Google Maps
- Neshan

Available access modes:

- Web
- API

The API key field is enabled only when API mode is selected. API credentials are entered at runtime and are not stored in the repository or embedded in the executable.

Current implementation status:

- Google Maps Web: available.
- Google Maps API: available when a valid Google Maps API key is supplied.
- Neshan Web: available.
- Neshan API: available when a valid Neshan API key is supplied.
