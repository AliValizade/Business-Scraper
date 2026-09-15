import sys

from app.composition import create_application
from browser.manager import BrowserManager
from cli.commands import (
    format_scrape_result,
    run_scrape_command,
)
from cli.parser import create_parser
from database.database import SessionLocal


def create_cli_application(source):
    """Create the application used by the CLI."""

    browser_manager = BrowserManager()

    return create_application(
        session_factory=SessionLocal,
        browser_manager=browser_manager,
        source=source,
    )


def main(argv=None):
    """Run the command-line application."""

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

        print(
            format_scrape_result(result)
        )

        return result

    parser.error(
        f"Unknown command: {args.command}"
    )


if __name__ == "__main__":
    main(sys.argv[1:])