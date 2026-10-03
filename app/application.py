from core.result import ScrapeResult
from services.business_service import BusinessService
from services.export_service import ExportService as ApplicationExportService
from services.license_service import LicenseService
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
        scrape_service=None,
        run_service=None,
        business_service=None,
        application_export_service=None,
        license_service=None,
    ):
        if pipeline is None:
            raise ValueError("pipeline is required.")

        self.pipeline = pipeline
        self.registry = registry
        self.factory = factory
        self.export_service = export_service
        self.session_factory = session_factory

        self.scrape_service = scrape_service or ScrapeService(pipeline=pipeline)

        self.run_service = (
            run_service
            if run_service is not None
            else (
                RunService(session_factory=session_factory)
                if session_factory is not None
                else None
            )
        )
        self.business_service = (
            business_service
            if business_service is not None
            else (
                BusinessService(session_factory=session_factory)
                if session_factory is not None
                else None
            )
        )
        self.application_export_service = (
            application_export_service
            if application_export_service is not None
            else (
                ApplicationExportService(
                    export_service=export_service,
                    run_service=self.run_service,
                )
                if export_service is not None and self.run_service is not None
                else None
            )
        )
        self.license_service = license_service or LicenseService()

    def run(self, location, keywords, max_results=None, source=None, access_mode=None, api_key=None):
        configured_source = getattr(self.pipeline, "source", "google_maps")
        if not isinstance(configured_source, str):
            configured_source = "google_maps"

        configured_mode = getattr(
            getattr(self.pipeline, "scraper", None),
            "access_mode",
            "web",
        )
        if not isinstance(configured_mode, str):
            configured_mode = "web"

        source = configured_source if source is None else source
        access_mode = configured_mode if access_mode is None else access_mode

        legacy_defaults = (
            source == "google_maps"
            and access_mode == "web"
            and api_key is None
        )

        if legacy_defaults:
            result = self.scrape_service.start_scrape(
                location=location,
                keywords=keywords,
                max_results=max_results,
            )
        else:
            result = self.scrape_service.start_scrape(
                location=location,
                keywords=keywords,
                max_results=max_results,
                source=source,
                access_mode=access_mode,
                api_key=api_key,
            )

        if isinstance(result, ScrapeResult):
            return result

        return ScrapeResult(
            status=result.status,
            source=result.source,
            access_mode=result.access_mode,
            location=result.location,
            keywords=result.keywords,
            run_id=result.run_id,
            total_found=result.total_found,
            total_new=result.total_new,
            total_updated=result.total_updated,
            total_duplicates=result.total_duplicates,
            total_errors=result.total_errors,
            error_message=result.error_message,
        )

    def export(self, data, output_path, format_name, metadata=None):
        if self.export_service is None:
            raise ValueError("export_service is not configured.")

        if self.application_export_service is not None:
            result = self.application_export_service.export(
                data=data,
                output_path=output_path,
                format_name=format_name,
                metadata=metadata,
            )
            return result.output_path

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
                    "access_mode",
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
        return [
            {field: getattr(business, field) for field in business.__dataclass_fields__}
            for business in self.business_service.list_businesses()
        ]

    def get_run(self, run_id):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        run = self.run_service.get_run(run_id)
        return {field: getattr(run, field) for field in run.__dataclass_fields__}

    def get_run_businesses(self, run_id):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        return [
            {field: getattr(business, field) for field in business.__dataclass_fields__}
            for business in self.run_service.get_run_businesses(run_id)
        ]

    def list_runs(self, limit=DEFAULT_RUN_HISTORY_LIMIT):
        if self.run_service is None:
            raise ValueError("session_factory is not configured.")
        return [
            {field: getattr(run, field) for field in run.__dataclass_fields__}
            for run in self.run_service.list_runs(limit=limit)
        ]
