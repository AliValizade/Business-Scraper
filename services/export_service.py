from .dto import ExportResultDTO


class ExportService:
    """Application service boundary for export operations."""

    def __init__(self, export_service, run_service):
        if export_service is None:
            raise ValueError("export_service is required.")
        if run_service is None:
            raise ValueError("run_service is required.")
        self.exporter = export_service
        self.run_service = run_service

    def export(self, data, output_path, format_name, metadata=None):
        if metadata is None:
            result = self.exporter.export(
                data=data,
                output_path=output_path,
                format_name=format_name,
            )
        else:
            result = self.exporter.export(
                data=data,
                output_path=output_path,
                format_name=format_name,
                metadata=metadata,
            )
        return ExportResultDTO(
            output_path=result,
            format_name=format_name,
            exported_count=len(data),
        )

    def export_run(self, run_id, output_path, format_name):
        businesses = self.run_service.get_run_businesses(run_id)
        metadata = None

        if format_name.strip().lower() == "excel":
            run = self.run_service.get_run(run_id)
            metadata = {
                key: getattr(run, key)
                for key in (
                    "source",
                    "city",
                    "keyword",
                    "started_at",
                    "finished_at",
                    "status",
                    "total_found",
                    "total_new",
                    "total_updated",
                    "total_duplicates",
                    "total_errors",
                    "error_message",
                )
            }
            metadata["exported_businesses"] = len(businesses)

        return self.export(
            data=[business.__dict__ if hasattr(business, "__dict__") else business for business in businesses],
            output_path=output_path,
            format_name=format_name,
            metadata=metadata,
        )
