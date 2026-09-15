def run_scrape_command(args, application):
    """Execute the scrape CLI command."""

    return application.run(
        location=args.location,
        keywords=args.keywords,
    )


def format_scrape_result(result):
    """Format a scrape result for CLI output."""

    lines = [
        f"Status: {result.get('status', 'UNKNOWN')}",
        f"Found: {result.get('total_found', 0)}",
        f"New: {result.get('total_new', 0)}",
        f"Updated: {result.get('total_updated', 0)}",
        f"Duplicates: {result.get('total_duplicates', 0)}",
        f"Errors: {result.get('total_errors', 0)}",
    ]

    return "\n".join(lines)