import argparse


def positive_int(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc

    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")

    return number


def create_parser():
    parser = argparse.ArgumentParser(
        prog="business-scraper",
        description="Modular business web scraper.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape business data.",
    )

    scrape_parser.add_argument(
        "--source",
        default="google_maps",
        help="Scraper source.",
    )

    scrape_parser.add_argument(
        "--location",
        required=True,
        help="Search location.",
    )

    scrape_parser.add_argument(
        "--keyword",
        action="append",
        required=True,
        dest="keywords",
        help="Search keyword. Can be specified multiple times.",
    )

    scrape_parser.add_argument(
        "--max-results",
        type=positive_int,
        default=None,
        help="Maximum number of results for the entire request.",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="Export business data.",
    )

    export_parser.add_argument(
        "--format",
        required=True,
        choices=["csv", "json", "excel"],
        dest="format_name",
        help="Export format.",
    )

    export_parser.add_argument(
        "--run-id",
        type=positive_int,
        default=None,
        dest="run_id",
        help="Export businesses associated with a specific scrape run.",
    )

    export_parser.add_argument(
        "--output",
        required=True,
        dest="output_path",
        help="Output file path.",
    )

    runs_parser = subparsers.add_parser(
        "runs",
        help="List recent scrape runs.",
    )

    runs_parser.add_argument(
        "--limit",
        type=positive_int,
        default=20,
        help="Maximum number of runs to display.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Show a scrape run by ID.",
    )

    run_parser.add_argument(
        "run_id",
        type=positive_int,
        help="Scrape run ID.",
    )

    run_parser.add_argument(
        "--businesses",
        action="store_true",
        help="Show businesses associated with the scrape run.",
    )

    return parser
