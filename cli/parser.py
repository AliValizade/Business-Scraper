import argparse


def create_parser():
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="business-scraper",
        description=(
            "Modular business web scraper."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape businesses from a source.",
    )

    scrape_parser.add_argument(
        "--source",
        default="google_maps",
        help=(
            "Scraping source. "
            "Default: google_maps"
        ),
    )

    scrape_parser.add_argument(
        "--location",
        required=True,
        help="City or geographic location.",
    )

    scrape_parser.add_argument(
        "--keyword",
        action="append",
        required=True,
        dest="keywords",
        help=(
            "Search keyword. "
            "Repeat this option for multiple keywords."
        ),
    )

    return parser
