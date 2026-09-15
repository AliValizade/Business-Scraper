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

    def run(self, location, keywords, max_results=None):
        request = ScrapeRequest(
            location=location,
            keywords=keywords,
            max_results=max_results,
        )
        return self.pipeline.run(request=request)

        