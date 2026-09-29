from core.errors import RunNotFoundError


class RunService:
    """Application service boundary for scrape-run operations."""

    DEFAULT_RUN_HISTORY_LIMIT = 20

    def __init__(self, session_factory):
        if session_factory is None:
            raise ValueError("session_factory is required.")
        self.session_factory = session_factory

    def get_run(self, run_id):
        self._validate_run_id(run_id)
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
            return [self._run_to_dict(run) for run in runs]
        finally:
            session.close()

    def get_run_businesses(self, run_id):
        self._validate_run_id(run_id)
        from core.models import Business, ScrapeRun, ScrapeRunBusiness

        session = self.session_factory()
        try:
            scrape_run = (
                session.query(ScrapeRun)
                .filter(ScrapeRun.id == run_id)
                .one_or_none()
            )
            if scrape_run is None:
                raise RunNotFoundError(run_id)

            businesses = (
                session.query(Business)
                .join(
                    ScrapeRunBusiness,
                    ScrapeRunBusiness.business_id == Business.id,
                )
                .filter(ScrapeRunBusiness.run_id == run_id)
                .order_by(Business.id.asc())
                .all()
            )
            return [self._business_to_dict(business) for business in businesses]
        finally:
            session.close()

    @staticmethod
    def _validate_run_id(run_id):
        if not isinstance(run_id, int) or isinstance(run_id, bool):
            raise TypeError("run_id must be an integer.")
        if run_id <= 0:
            raise ValueError("run_id must be greater than zero.")

    @staticmethod
    def _run_to_dict(scrape_run):
        return {
            column.name: getattr(scrape_run, column.name)
            for column in scrape_run.__table__.columns
        }

    @staticmethod
    def _business_to_dict(business):
        return {
            column.name: getattr(business, column.name)
            for column in business.__table__.columns
        }
