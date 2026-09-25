from core.request import ScrapeRequest
from core.errors import RunNotFoundError


class Application:
    """Application-level orchestration for scraping and export use cases."""

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

    def run(
        self,
        location,
        keywords,
        max_results=None,
    ):
        request = ScrapeRequest(
            location=location,
            keywords=keywords,
            max_results=max_results,
        )

        return self.pipeline.run(request=request)

    def export(
        self,
        data,
        output_path,
        format_name,
    ):
        if self.export_service is None:
            raise ValueError("export_service is not configured.")

        return self.export_service.export(
            data=data,
            output_path=output_path,
            format_name=format_name,
        )

    def get_businesses(self):
        if self.session_factory is None:
            raise ValueError(
                "session_factory is not configured."
            )

        from core.models import Business

        session = self.session_factory()

        try:
            businesses = session.query(Business).all()

            return [
                {
                    column.name: getattr(business, column.name)
                    for column in Business.__table__.columns
                }
                for business in businesses
            ]
        finally:
            session.close()

    def get_run(self, run_id):
        if self.session_factory is None:
            raise ValueError(
                "session_factory is not configured."
            )

        if not isinstance(run_id, int) or isinstance(run_id, bool):
            raise TypeError("run_id must be an integer.")

        if run_id <= 0:
            raise ValueError("run_id must be greater than zero.")

        from core.models import ScrapeRun

        session = self.session_factory()

        try:
            scrape_run = (
                session.query(ScrapeRun)
                .filter(ScrapeRun.id == run_id)
                .one_or_none()
            )

            if scrape_run is None:
                raise RunNotFoundError(run_id)

            return self._run_to_dict(scrape_run)
        finally:
            session.close()

    def list_runs(self, limit=DEFAULT_RUN_HISTORY_LIMIT):
        if self.session_factory is None:
            raise ValueError(
                "session_factory is not configured."
            )

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer.")

        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        from core.models import ScrapeRun

        session = self.session_factory()

        try:
            runs = (
                session.query(ScrapeRun)
                .order_by(
                    ScrapeRun.started_at.desc(),
                    ScrapeRun.id.desc(),
                )
                .limit(limit)
                .all()
            )

            return [
                self._run_to_dict(scrape_run)
                for scrape_run in runs
            ]
        finally:
            session.close()

    @staticmethod
    def _run_to_dict(scrape_run):
        return {
            column.name: getattr(scrape_run, column.name)
            for column in scrape_run.__table__.columns
        }
