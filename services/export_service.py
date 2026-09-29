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
            return self.exporter.export(
                data=data,
                output_path=output_path,
                format_name=format_name,
            )
        return self.exporter.export(
            data=data,
            output_path=output_path,
            format_name=format_name,
            metadata=metadata,
        )

    def export_run(self, run_id, output_path, format_name):
        businesses = self.run_service.get_run_businesses(run_id)
        metadata = None

        if format_name.strip().lower() == "excel":
            run = self.run_service.get_run(run_id)
            metadata = {
                key: run.get(key)
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
            data=businesses,
            output_path=output_path,
            format_name=format_name,
            metadata=metadata,
        )
