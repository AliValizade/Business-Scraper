import argparse


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
        type=int,
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
        "--output",
        required=True,
        dest="output_path",
        help="Output file path.",
    )

    return parser