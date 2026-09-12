import re
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

        results_container = self.page.locator(
            'div[role="feed"]'
        )

        results_container.wait_for(
            state="visible",
            timeout=30000
        )

        result_cards = results_container.locator(
            'div[role="article"]'
        )

        result_count = result_cards.count()

        print("\n--- Google Maps Results Inspection ---")
        print(
            f"Results container found: "
            f"{results_container.count() > 0}"
        )
        print(f"Business cards found: {result_count}")

        if result_count > 0:
            first_card = result_cards.nth(0)

            print("\n--- First Business Card ---")
            print(first_card.inner_text())

        return {
            "container_found": results_container.count() > 0,
            "result_count": result_count,
        }

    def extract_first_business(self):
        if self.page is None:
            raise RuntimeError(
                "Search must be performed before extraction."
            )

        results_container = self.page.locator(
            'div[role="feed"]'
        )

        results_container.wait_for(
            state="visible",
            timeout=30000
        )

        result_cards = results_container.locator(
            'div[role="article"]'
        )

        if result_cards.count() == 0:
            return None

        card = result_cards.nth(0)

        # -------------------------
        # Name
        # -------------------------
        name = None

        name_locator = card.locator(
            'a[aria-label]'
        ).first

        if name_locator.count() > 0:
            name = name_locator.get_attribute("aria-label")

        if not name:
            heading = card.locator(
                '[role="heading"]'
            ).first

            if heading.count() > 0:
                name = heading.inner_text().strip()

        # -------------------------
        # Raw text
        # -------------------------
        lines = [
            line.strip()
            for line in card.inner_text().splitlines()
            if line.strip()
        ]

        raw_text = "\n".join(lines)

        # -------------------------
        # Rating
        # -------------------------
        rating = None

        rating_match = re.search(
            r'(?<!\d)([0-5](?:[.,]\d)?)(?!\d)',
            raw_text
        )

        if rating_match:
            rating = float(
                rating_match.group(1).replace(",", ".")
            )

        # -------------------------
        # Reviews count
        # -------------------------
        reviews_count = None

        reviews_match = re.search(
            r'\(([\d,.\u0660-\u0669\u06F0-\u06F9]+)\)',
            raw_text
        )

        if reviews_match:
            reviews_text = reviews_match.group(1)

            reviews_text = (
                reviews_text
                .replace(",", "")
                .replace(".", "")
                .translate(
                    str.maketrans(
                        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
                        "01234567890123456789"
                    )
                )
            )

            try:
                reviews_count = int(reviews_text)
            except ValueError:
                reviews_count = None

        # -------------------------
        # Address
        # -------------------------
        address = None

        for line in lines:
            if "·" in line:
                parts = [
                    part.strip()
                    for part in line.split("·")
                    if part.strip()
                ]

                if len(parts) >= 2:
                    possible_address = parts[-1]

                    if (
                        possible_address != name
                        and not possible_address.lower().startswith(
                            ("open", "closed")
                        )
                    ):
                        address = possible_address
                        break

        business = {
            "name": name,
            "address": address,
            "rating": rating,
            "reviews_count": reviews_count,
        }

        return business

    def scrape(self):
        raise NotImplementedError(
            "Business extraction will be implemented in the next phase."
        )