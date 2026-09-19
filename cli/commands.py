def run_scrape_command(args, application):
    return application.run(
        location=args.location,
        keywords=args.keywords,
        max_results=args.max_results,
    )


def format_scrape_result(result):
    lines = [
        f"Status: {result.status}",
        f"Found: {result.total_found}",
        f"New: {result.total_new}",
        f"Updated: {result.total_updated}",
        f"Duplicates: {result.total_duplicates}",
        f"Errors: {result.total_errors}",
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