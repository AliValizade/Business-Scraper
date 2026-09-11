from urllib.parse import quote_plus

from scrapers.base import BaseScraper


class GoogleMapsScraper(BaseScraper):
    BASE_SEARCH_URL = "https://www.google.com/maps/search/"

    def search(self, query, location):
        search_query = f"{query} {location}".strip()
        encoded_query = quote_plus(search_query)

        url = f"{self.BASE_SEARCH_URL}?api=1&query={encoded_query}"

        if self.browser_manager.page is None:
            raise RuntimeError(
                "BrowserManager must be started before searching."
            )

        self.page = self.browser_manager.page

        self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return self.page

    def scrape(self):
        raise NotImplementedError(
            "Business extraction will be implemented in the next phase."
        )