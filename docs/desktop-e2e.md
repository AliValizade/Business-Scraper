# Desktop E2E Validation

Phase 4.5 validates the complete desktop delivery path without changing the
application architecture.

## Automated contract validation

Run:

```bash
pytest -q
```

The desktop E2E contract tests verify:

- the desktop entrypoint initializes the database and composes the application;
- persistent licensing is wired into the desktop composition;
- the PyInstaller spec bundles `ms-playwright`;
- the Inno Setup definition consumes the one-file executable;
- packaging documentation matches the build contract;
- the UI exposes scrape, export, and repeat-scrape flows;
- the application prevents closing while a scrape is running.

## Manual acceptance flow

The following must be validated on a Windows machine:

1. Run `python desktop.py`.
2. Enter location, keywords, and max results.
3. Start a scrape and verify Chromium opens and results appear.
4. Start a second scrape without restarting the application.
5. Select a completed run and export CSV, JSON, and Excel.
6. Activate a license, close the application, reopen it, and verify the
   license remains active.
7. Build the executable with:

   ```bash
   playwright install chromium
   pyinstaller --clean --noconfirm Business-Scraper.spec
   ```

8. Run `dist/Business-Scraper.exe` from a console and repeat the scrape
   and export checks.
9. Build and install the Inno Setup package and repeat the same checks from
   the installed application.

## Clean-machine acceptance

For final release validation, install the generated Inno Setup package on a
Windows machine without the development Python environment or repository
checkout. The installed application must start, open bundled Chromium, scrape,
persist run history, export data, and retain the local license state.

A clean-machine run is a release acceptance step; it is not replaced by the
automated contract tests.
