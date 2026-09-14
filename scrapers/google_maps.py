import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote_plus
from scrapers.base import BaseScraper
from core.states import ScraperState
from utils.logger import get_logger
from utils.retry import retry
from config import RETRY_COUNT, RETRY_DELAY


logger = get_logger(__name__)

class GoogleMapsScraper(BaseScraper):
    BASE_SEARCH_URL = "https://www.google.com/maps/search/"

    def __init__(self, browser_manager):
        super().__init__(browser_manager)

        self.search_keyword = None
        self.search_location = None

    def search(self, query, location):
        search_query = f"{query} {location}".strip()
        encoded_query = quote_plus(search_query)
        url = f"{self.BASE_SEARCH_URL}?api=1&query={encoded_query}"

        if self.browser_manager.page is None:
            self.set_state(ScraperState.FAILED)

            logger.error(
                "Browser page is not available | query=%s | location=%s",
                query,
                location,
            )

            raise RuntimeError(
                "BrowserManager must be started before searching."
            )

        self.set_state(ScraperState.SEARCHING)

        logger.info(
            "Google Maps search started | query=%s | location=%s",
            query,
            location,
        )

        self.page = self.browser_manager.page

        self.search_keyword = query
        self.search_location = location

        try:
            self.set_state(ScraperState.LOADING)

            retry(
                lambda: self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                ),
                retries=RETRY_COUNT,
                delay=RETRY_DELAY,
                exceptions=(
                    TimeoutError,
                    PlaywrightTimeoutError,
                ),
            )

            logger.info(
                "Google Maps page loaded | url=%s",
                self.page.url,
            )

            return self.page

        except Exception:
            self.set_state(ScraperState.FAILED)

            logger.exception(
                "Google Maps page load failed | "
                "query=%s | location=%s",
                query,
                location,
            )

            raise

    def _get_results_container(self):
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

        return results_container

    def _get_result_cards(self):
        results_container = self._get_results_container()

        return results_container.locator(
            'div[role="article"]'
        )

    def inspect_results(self):
        results_container = self._get_results_container()

        result_cards = results_container.locator(
            'div[role="article"]'
        )

        result_count = result_cards.count()

        print("\n--- Google Maps Results Inspection ---")
        print("Results container found: True")
        print(f"Business cards found: {result_count}")

        if result_count > 0:
            first_card = result_cards.nth(0)

            print("\n--- First Business Card ---")
            print(first_card.inner_text())

        return {
            "container_found": True,
            "result_count": result_count,
        }

    def _extract_business_url(self, card):
        link = card.locator(
            'a[href*="/maps/place/"]'
        ).first

        if link.count() == 0:
            return None

        href = link.get_attribute("href")

        if not href:
            return None

        return href

    def _extract_coordinates(self, google_maps_url):
        if not google_maps_url:
            return None, None

        latitude = None
        longitude = None

        coordinate_match = re.search(
            r'!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)',
            google_maps_url
        )

        if coordinate_match:
            try:
                latitude = float(coordinate_match.group(1))
                longitude = float(coordinate_match.group(2))
            except ValueError:
                pass

        return latitude, longitude

    def _extract_phone(self, card):
        phone = None

        phone_link = card.locator(
            'a[href^="tel:"]'
        ).first

        if phone_link.count() > 0:
            href = phone_link.get_attribute("href")

            if href:
                phone = href.replace(
                    "tel:",
                    "",
                    1
                ).strip()

        if phone:
            return phone

        text = card.inner_text()

        phone_patterns = [
            r'\+98[\s\-()]*9\d{9}',
            r'0098[\s\-()]*9\d{9}',
            r'09\d{9}',
            r'\+98[\s\-()]*\d{2,3}[\s\-()]*\d{7,8}',
            r'0\d{2,3}[\s\-()]*\d{7,8}',
        ]

        for pattern in phone_patterns:
            match = re.search(
                pattern,
                text
            )

            if match:
                phone = match.group(0).strip()
                break

        return phone

    def _extract_website(self, card):
        website = None

        links = card.locator("a")

        link_count = links.count()

        for index in range(link_count):
            link = links.nth(index)

            href = link.get_attribute("href")

            if not href:
                continue

            href_lower = href.lower()

            if href_lower.startswith("tel:"):
                continue

            if "/maps/" in href_lower:
                continue

            if "google.com" in href_lower:
                continue

            if href_lower.startswith(
                ("http://", "https://")
            ):
                website = href
                break

        return website

    def _extract_business_from_card(self, card):
        lines = [
            line.strip()
            for line in card.inner_text().splitlines()
            if line.strip()
        ]

        raw_text = "\n".join(lines)

        # ----------------------------------------
        # Name
        # ----------------------------------------

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

        # ----------------------------------------
        # Category / Address
        # ----------------------------------------

        category = None
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

            possible_category = parts[0]
            possible_address = parts[-1]

            if possible_category != name:
                category = possible_category

            if possible_address != name:
                if not possible_address.lower().startswith(
                    ("open", "closed")
                ):
                    address = possible_address

            if category or address:
                break

        # ----------------------------------------
        # Rating
        # ----------------------------------------

        rating = None

        rating_match = re.search(
            r'(?<!\d)([0-5](?:[.,]\d)?)(?!\d)',
            raw_text
        )

        if rating_match:
            try:
                rating = float(
                    rating_match.group(1).replace(",", ".")
                )
            except ValueError:
                rating = None

        # ----------------------------------------
        # Reviews Count
        # ----------------------------------------

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

        # ----------------------------------------
        # Google Maps URL
        # ----------------------------------------

        google_maps_url = self._extract_business_url(
            card
        )

        # ----------------------------------------
        # Coordinates
        # ----------------------------------------

        latitude, longitude = self._extract_coordinates(
            google_maps_url
        )

        # ----------------------------------------
        # Phone
        # ----------------------------------------

        phone = self._extract_phone(card)

        # ----------------------------------------
        # Website
        # ----------------------------------------

        website = self._extract_website(card)

        # ----------------------------------------
        # Source ID
        # ----------------------------------------

        source_id = None

        # ----------------------------------------
        # Structured Business Data
        # ----------------------------------------

        return {
            "name": name,
            "category": category,
            "address": address,
            "phone": phone,
            "website": website,
            "rating": rating,
            "reviews_count": reviews_count,
            "latitude": latitude,
            "longitude": longitude,
            "source": "google_maps",
            "source_id": source_id,
            "source_url": self.page.url,
            "google_maps_url": google_maps_url,
            "search_keyword": self.search_keyword,
            "city": self.search_location,
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
                business = self._extract_business_from_card(
                    card
                )

                businesses.append(business)

            except Exception as error:
                print(
                    f"Error extracting business "
                    f"{index + 1}: {error}"
                )

        return businesses

    def scroll_results(
        self,
        max_results=30,
        max_scroll_attempts=10,
        wait_time=2000,
    ):
        results_container = self._get_results_container()

        self.set_state(ScraperState.SCROLLING)

        logger.info(
            "Google Maps result scrolling started | "
            "max_results=%s | max_scroll_attempts=%s",
            max_results,
            max_scroll_attempts,
        )

        businesses = []
        seen_names = set()

        scroll_attempt = 0

        print("\n--- Scrolling Google Maps Results ---")

        while (
            len(businesses) < max_results
            and scroll_attempt < max_scroll_attempts
        ):
            result_cards = results_container.locator(
                'div[role="article"]'
            )

            current_count = result_cards.count()

            print(
                f"Scroll {scroll_attempt + 1}: "
                f"{current_count} cards loaded"
            )

            self.set_state(ScraperState.EXTRACTING)

            for index in range(current_count):
                if len(businesses) >= max_results:
                    break

                try:
                    card = result_cards.nth(index)

                    business = self._extract_business_from_card(
                        card
                    )

                    name = business.get("name")

                    if not name:
                        continue

                    if name in seen_names:
                        continue

                    seen_names.add(name)
                    businesses.append(business)

                except Exception as error:
                    print(
                        f"Error extracting card "
                        f"{index + 1}: {error}"
                    )

            if len(businesses) >= max_results:
                break

            previous_count = current_count

            results_container.evaluate(
                """
                element => {
                    element.scrollTop = element.scrollHeight;
                }
                """
            )

            self.page.wait_for_timeout(wait_time)

            result_cards = results_container.locator(
                'div[role="article"]'
            )

            new_count = result_cards.count()

            if new_count == previous_count:
                print(
                    "No new results loaded. "
                    "Stopping scroll."
                )
                break

            scroll_attempt += 1

        print(
            f"\nTotal unique businesses collected: "
            f"{len(businesses)}"
        )

        self.set_state(ScraperState.COMPLETED)

        logger.info(
            "Google Maps scraping completed | "
            "businesses_collected=%s",
            len(businesses),
        )
        
        return businesses

    def scrape(self):
        from config import (
            MAX_RESULTS,
            MAX_SCROLL_ATTEMPTS,
            SCROLL_WAIT_TIME,
        )

        return self.scroll_results(
            max_results=MAX_RESULTS,
            max_scroll_attempts=MAX_SCROLL_ATTEMPTS,
            wait_time=SCROLL_WAIT_TIME,
        )