from core.request import ScrapeRequest


class Application:
    """Application-level orchestration for scraping and export use cases."""

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