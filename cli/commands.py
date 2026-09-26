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


def run_list_runs_command(args, application):
    return application.list_runs(
        limit=args.limit,
    )


def run_get_run_command(args, application):
    return application.get_run(
        run_id=args.run_id,
    )


def format_run(run):
    return "\n".join(
        [
            f"ID: {run['id']}",
            f"Source: {run['source']}",
            f"City: {run['city']}",
            f"Keyword: {run['keyword']}",
            f"Started: {run['started_at']}",
            f"Finished: {run['finished_at']}",
            f"Status: {run['status']}",
            f"Found: {run['total_found']}",
            f"New: {run['total_new']}",
            f"Updated: {run['total_updated']}",
            f"Duplicates: {run['total_duplicates']}",
            f"Errors: {run['total_errors']}",
            f"Error: {run['error_message']}",
        ]
    )


def format_runs(runs):
    if not runs:
        return "No scrape runs found."

    return "\n\n".join(
        format_run(run)
        for run in runs
    )
