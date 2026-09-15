def run_scrape_command(args, application):
    return application.run(
        location=args.location,
        keywords=args.keywords,
        max_results=args.max_results,
    )


def format_scrape_result(result):
    lines = [
        f"Status: {result.get('status', 'UNKNOWN')}",
        f"Found: {result.get('total_found', 0)}",
        f"New: {result.get('total_new', 0)}",
        f"Updated: {result.get('total_updated', 0)}",
        f"Duplicates: {result.get('total_duplicates', 0)}",
        f"Errors: {result.get('total_errors', 0)}",
    ]

    return "\n".join(lines)


def run_export_command(args, application, data):
    return application.export(
        data=data,
        output_path=args.output_path,
        format_name=args.format_name,
    )


def format_export_result(result, format_name):
    return (
        f"Export completed successfully.\n"
        f"Format: {format_name}\n"
        f"Output: {result}"
    )