from core.request import ScrapeRequest


class Application:
    """Application-level orchestration for scraping use cases."""

    def __init__(
        self,
        pipeline,
        registry=None,
        factory=None,
    ):
        if pipeline is None:
            raise ValueError(
                "pipeline is required."
            )

        self.pipeline = pipeline
        self.registry = registry
        self.factory = factory

    def run(
        self,
        location,
        keywords,
    ):
        """Create a scrape request and execute the pipeline."""

        request = ScrapeRequest(
            location=location,
            keywords=keywords,
        )

        return self.pipeline.run(
            request=request,
        )


        