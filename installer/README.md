# Desktop Installer

## Build

1. Build the PyInstaller application from the repository root:

```text
pyinstaller --clean --noconfirm Business-Scraper.spec
```

2. Install Inno Setup on the build machine.

3. Open `installer/Business-Scraper.iss` with Inno Setup Compiler and build the installer.

The expected PyInstaller output directory is:

```text
dist/Business-Scraper/
```

The installer output is:

```text
dist/installer/
```

## First run

The desktop entrypoint initializes the SQLite schema before creating the application. The installer does not ship a pre-existing database.

The current application keeps its SQLite database under the application's database directory. Moving persistent user data to an OS-specific user-data directory is intentionally deferred until a concrete packaging validation requires it, to avoid an unnecessary domain/infrastructure refactor.

## Uninstall

The installer removes the installed application files. User-created database/export data is not explicitly deleted by the installer.
