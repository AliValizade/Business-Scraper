def run_scrape_command(args, application):
    service = getattr(application, "scrape_service", None)

    if service is not None:
        return service.start_scrape(
            location=args.location,
            keywords=args.keywords,
            max_results=args.max_results,
        )

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


def run_export_command(args, application, data=None):
    if getattr(args, "run_id", None) is not None:
        service = getattr(application, "application_export_service", application)
        return service.export_run(
            run_id=args.run_id,
            output_path=args.output_path,
            format_name=args.format_name,
        )

    if data is None:
        service = getattr(application, "business_service", application)
        businesses = service.list_businesses()
        data = [
            {
                field: getattr(business, field)
                for field in business.__dataclass_fields__
            }
            if hasattr(business, "__dataclass_fields__")
            else business
            for business in businesses
        ]

    service = getattr(application, "application_export_service", application)
    return service.export(
        data=data,
        output_path=args.output_path,
        format_name=args.format_name,
    )


def format_export_result(result, format_name):
    output_path = getattr(result, "output_path", result)
    return (
        f"Export completed successfully.\n"
        f"Format: {format_name}\n"
        f"Output: {output_path}"
    )


def run_list_runs_command(args, application):
    service = getattr(application, "run_service", application)
    result = service.list_runs(limit=args.limit)
    return [
        {
            field: getattr(run, field)
            for field in run.__dataclass_fields__
        }
        if hasattr(run, "__dataclass_fields__")
        else run
        for run in result
    ]


def run_get_run_command(args, application):
    service = getattr(application, "run_service", application)
    result = service.get_run(run_id=args.run_id)
    if hasattr(result, "__dataclass_fields__"):
        return {
            field: getattr(result, field)
            for field in result.__dataclass_fields__
        }
    return result


def run_get_run_businesses_command(args, application):
    service = getattr(application, "run_service", application)
    result = service.get_run_businesses(run_id=args.run_id)
    return [
        {
            field: getattr(business, field)
            for field in business.__dataclass_fields__
        }
        if hasattr(business, "__dataclass_fields__")
        else business
        for business in result
    ]


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


def format_run_businesses(businesses):
    if not businesses:
        return "No businesses found for this run."

    return "\n\n".join(
        "\n".join(
            [
                f"ID: {business['id']}",
                f"Name: {business['name']}",
                f"Category: {business['category']}",
                f"City: {business['city']}",
                f"Address: {business['address']}",
                f"Phone: {business['phone']}",
                f"Rating: {business['rating']}",
                f"Reviews: {business['reviews_count']}",
                f"Source: {business['source']}",
                f"URL: {business['google_maps_url']}",
            ]
        )
        for business in businesses
    )


def format_runs(runs):
    if not runs:
        return "No scrape runs found."

    return "\n\n".join(
        format_run(run)
        for run in runs
    )
