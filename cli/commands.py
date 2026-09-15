def run_scrape_command(args, application):
    """Execute the scrape CLI command."""

    result = application.run(
        location=args.location,
        keywords=args.keywords,
    )

    return result
