from core.errors import RunNotFoundError

from .dto import BusinessDTO, RunDTO


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
            return self._run_to_dto(scrape_run)
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
            return [self._run_to_dto(run) for run in runs]
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
            return [self._business_to_dto(business) for business in businesses]
        finally:
            session.close()

    @staticmethod
    def _validate_run_id(run_id):
        if not isinstance(run_id, int) or isinstance(run_id, bool):
            raise TypeError("run_id must be an integer.")
        if run_id <= 0:
            raise ValueError("run_id must be greater than zero.")

    @staticmethod
    def _run_to_dto(scrape_run):
        return RunDTO(
            id=scrape_run.id,
            source=scrape_run.source,
            access_mode=scrape_run.access_mode,
            city=scrape_run.city,
            keyword=scrape_run.keyword,
            started_at=scrape_run.started_at,
            finished_at=scrape_run.finished_at,
            status=scrape_run.status,
            total_found=scrape_run.total_found,
            total_new=scrape_run.total_new,
            total_updated=scrape_run.total_updated,
            total_duplicates=scrape_run.total_duplicates,
            total_errors=scrape_run.total_errors,
            error_message=scrape_run.error_message,
        )

    @staticmethod
    def _business_to_dto(business):
        return BusinessDTO(
            id=business.id,
            name=business.name,
            category=business.category,
            address=business.address,
            city=business.city,
            phone=business.phone,
            website=business.website,
            instagram=business.instagram,
            rating=business.rating,
            reviews_count=business.reviews_count,
            latitude=business.latitude,
            longitude=business.longitude,
            google_maps_url=business.google_maps_url,
            source=business.source,
            source_id=business.source_id,
            search_keyword=business.search_keyword,
            scraped_at=business.scraped_at,
            source_url=business.source_url,
            created_at=business.created_at,
            updated_at=business.updated_at,
        )
