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

    def _get_result_cards(self):
        if self.page is None:
            raise RuntimeError(
                "Search must be performed before extracting results."
            )

        results_container = self.page.locator(
            'div[role="feed"]'
        )

        results_container.wait_for(
            state="visible",
            timeout=30000
        )

        return results_container.locator(
            'div[role="article"]'
        )

    def inspect_results(self):
        result_cards = self._get_result_cards()

        result_count = result_cards.count()

        print("\n--- Google Maps Results Inspection ---")
        print(f"Results container found: True")
        print(f"Business cards found: {result_count}")

        if result_count > 0:
            first_card = result_cards.nth(0)

            print("\n--- First Business Card ---")
            print(first_card.inner_text())

        return {
            "container_found": True,
            "result_count": result_count,
        }

    def _extract_business_from_card(self, card):
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
        # Name
        # -------------------------
        name = None

        heading = card.locator(
            '[role="heading"]'
        ).first

        if heading.count() > 0:
            name = heading.inner_text().strip()

        if not name:
            name_locator = card.locator(
                'a[aria-label]'
            ).first

            if name_locator.count() > 0:
                name = name_locator.get_attribute(
                    "aria-label"
                )

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
        # Reviews Count
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
            if "·" not in line:
                continue

            parts = [
                part.strip()
                for part in line.split("·")
                if part.strip()
            ]

            if len(parts) < 2:
                continue

            possible_address = parts[-1]

            if possible_address == name:
                continue

            if possible_address.lower().startswith(
                ("open", "closed")
            ):
                continue

            address = possible_address
            break

        return {
            "name": name,
            "address": address,
            "rating": rating,
            "reviews_count": reviews_count,
        }

    def extract_first_business(self):
        result_cards = self._get_result_cards()

        if result_cards.count() == 0:
            return None

        return self._extract_business_from_card(
            result_cards.nth(0)
        )

    def extract_businesses(self, limit=None):
        result_cards = self._get_result_cards()

        total_cards = result_cards.count()

        if limit is not None:
            total_cards = min(total_cards, limit)

        businesses = []

        for index in range(total_cards):
            card = result_cards.nth(index)

            try:
                business = self._extract_business_from_card(card)

                businesses.append(business)

            except Exception as error:
                print(
                    f"Error extracting business "
                    f"{index + 1}: {error}"
                )

        return businesses

    def scrape(self):
        raise NotImplementedError(
            "Full scraping workflow will be implemented "
            "in the next phase."
        )