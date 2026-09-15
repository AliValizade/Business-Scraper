from scrapers.base import BaseScraper


class ScraperRegistry:
    """Registry for scraper implementations."""

    def __init__(self):
        self._scrapers = {}

    def register(self, source, scraper_class):
        """Register a scraper class for a source."""
        if not isinstance(source, str):
            raise TypeError(
                "source must be a string."
            )

        source = source.strip()

        if not source:
            raise ValueError(
                "source cannot be empty."
            )

        if not isinstance(
            scraper_class,
            type,
        ):
            raise TypeError(
                "scraper_class must be a class."
            )

        if not issubclass(
            scraper_class,
            BaseScraper,
        ):
            raise TypeError(
                "scraper_class must inherit from BaseScraper."
            )

        if source in self._scrapers:
            raise ValueError(
                f"Scraper already registered for "
                f"source '{source}'."
            )

        self._scrapers[source] = scraper_class

    def get(self, source):
        """Return the registered scraper class."""
        if not isinstance(source, str):
            raise TypeError(
                "source must be a string."
            )

        source = source.strip()

        if not source:
            raise ValueError(
                "source cannot be empty."
            )

        try:
            return self._scrapers[source]
        except KeyError:
            raise KeyError(
                f"No scraper registered for "
                f"source '{source}'."
            )

    def create(self, source, **kwargs):
        """Create a scraper instance for a source."""
        scraper_class = self.get(source)

        return scraper_class(**kwargs)

    def has(self, source):
        """Return True if a source is registered."""
        if not isinstance(source, str):
            raise TypeError(
                "source must be a string."
            )

        source = source.strip()

        if not source:
            raise ValueError(
                "source cannot be empty."
            )

        return source in self._scrapers

    def sources(self):
        """Return registered source names."""
        return tuple(self._scrapers.keys())