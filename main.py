import sys

from app.composition import create_application
from browser.manager import BrowserManager
from cli.commands import (
    format_export_result,
    format_scrape_result,
    format_run,
    format_runs,
    run_export_command,
    run_get_run_command,
    run_list_runs_command,
    run_scrape_command,
)
from cli.parser import create_parser
from database.database import SessionLocal


def create_cli_application(source):
    browser_manager = BrowserManager()

    return create_application(
        session_factory=SessionLocal,
        browser_manager=browser_manager,
        source=source,
    )


def main(argv=None):
    parser = create_parser()

    args = parser.parse_args(argv)

    if args.command == "scrape":
        application = create_cli_application(
            source=args.source,
        )

        result = run_scrape_command(
            args,
            application,
        )

        print(format_scrape_result(result))

        return result

    if args.command == "export":
        application = create_cli_application(
            source="google_maps",
        )

        data = application.get_businesses()

        result = run_export_command(
            args,
            application,
            data,
        )

        print(
            format_export_result(
                result,
                args.format_name,
            )
        )

        return result

    if args.command == "runs":
        application = create_cli_application(
            source="google_maps",
        )

        runs = run_list_runs_command(
            args,
            application,
        )

        print(format_runs(runs))

        return runs

    if args.command == "run":
        application = create_cli_application(
            source="google_maps",
        )

        run = run_get_run_command(
            args,
            application,
        )

        print(format_run(run))

        return run

    parser.error(
        f"Unknown command: {args.command}"
    )


if __name__ == "__main__":
    main(sys.argv[1:])
