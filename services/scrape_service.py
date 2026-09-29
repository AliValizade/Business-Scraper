from core.request import ScrapeRequest


class ScrapeService:
    """Application service boundary for scrape operations."""

    def __init__(self, pipeline):
        if pipeline is None:
            raise ValueError("pipeline is required.")
        self.pipeline = pipeline

    def start_scrape(self, location, keywords, max_results=None):
        request = ScrapeRequest(
            location=location,
            keywords=keywords,
            max_results=max_results,
        )
        return self.pipeline.run(request=request)
