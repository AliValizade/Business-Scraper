from scrapers.registry import ScraperRegistry


class ScraperFactory:
    """Factory for creating scraper instances."""

    def __init__(
        self,
        registry: ScraperRegistry,
    ):
        if not isinstance(
            registry,
            ScraperRegistry,
        ):
            raise TypeError(
                "registry must be an instance of ScraperRegistry."
            )

        self.registry = registry

    def create(
        self,
        source,
        **kwargs,
    ):
        """Create a scraper instance for the given source."""
        return self.registry.create(
            source,
            **kwargs,
        )