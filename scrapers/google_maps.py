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

    def inspect_results(self):
        if self.page is None:
            raise RuntimeError(
                "Search must be performed before inspecting results."
            )

        # Main Google Maps results container
        results_container = self.page.locator(
            'div[role="feed"]'
        )

        results_container.wait_for(
            state="visible",
            timeout=30000
        )

        # Business result cards
        result_cards = results_container.locator(
            'div[role="article"]'
        )

        result_count = result_cards.count()

        print("\n--- Google Maps Results Inspection ---")
        print(f"Results container found: {results_container.count() > 0}")
        print(f"Business cards found: {result_count}")

        if result_count > 0:
            first_card = result_cards.nth(0)

            print("\n--- First Business Card ---")
            print(first_card.inner_text())

        return {
            "container_found": results_container.count() > 0,
            "result_count": result_count,
        }

    def scrape(self):
        raise NotImplementedError(
            "Business extraction will be implemented in the next phase."
        )