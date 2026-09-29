from services.business_service import BusinessService
from services.export_service import ExportService as ApplicationExportService
from services.run_service import RunService
from services.scrape_service import ScrapeService


class Application:
    """Backward-compatible application facade over the Service Layer."""

    DEFAULT_RUN_HISTORY_LIMIT = 20

    def __init__(
        self,
        pipeline,
        registry=None,
        factory=None,
        export_service=None,
        session_factory=None,
    ):
        if pipeline is None:
            raise ValueError("pipeline is required.")

        self.pipeline = pipeline
        self.registry = registry
        self.factory = factory
        self.export_service = export_service
        self.session_factory = session_factory

        self.scrape_service = ScrapeService(pipeline=pipeline)

        self.run_service = None
        self.business_service = None
        self.application_export_service = None

        if session_factory is not None:
            self.run_service = RunService(session_factory=session_factory)
            self.business_service = BusinessService(
                session_factory=session_factory,
            )

        if export_service is not None and self.run_service is not None:
            self.application_export_service = ApplicationExportService(
                export_service=export_service,
                run_service=self.run_service,
            )

    def run(self, location, keywords, max_results=None):
        return self.scrape_service.start_scrape(
            location=location,
            keywords=keywords,
            max_results=max_results,
        )

    def export(self, data, output_path, format_name, metadata=None):
        if self.export_service is None:
            raise ValueError("export_service is not configured.")

        if metadata is None:
            return self.export_service.export(
                data=data,
                output_path=output_path,
                format_name=format_name,
            )

        return self.export_service.export(
            data=data,
            output_path=output_path,
            format_name=format_name,
            metadata=metadata,
        )

    def export_run(self, run_id, output_path, format_name):
        businesses = self.get_run_businesses(run_id)
        metadata = None

        if format_name.strip().lower() == "excel":
            run = self.get_run(run_id)
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

    def get_businesses(self):
        if self.business_service is None:
            raise ValueError("session_factory is not configured.")
        return self.business_service.list_businesses()

    def get_run(self, run_id):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        return self.run_service.get_run(run_id)

    def get_run_businesses(self, run_id):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        return self.run_service.get_run_businesses(run_id)

    def list_runs(self, limit=DEFAULT_RUN_HISTORY_LIMIT):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        return self.run_service.list_runs(limit=limit)
