import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from scrapers.base import BaseScraper
from core.states import ScraperState
from utils.logger import get_logger
from utils.retry import retry
from config import RETRY_COUNT, RETRY_DELAY


logger = get_logger(__name__)


class GoogleMapsAPIError(RuntimeError):
    """Raised when a Google Maps Places API request fails."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)



class GoogleMapsScraper(BaseScraper):
    BASE_SEARCH_URL = "https://www.google.com/maps/search/"
    PLACES_API_URL = "https://places.googleapis.com/v1/places:searchText"
    PLACES_FIELD_MASK = ",".join(
        (
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.nationalPhoneNumber",
            "places.internationalPhoneNumber",
            "places.websiteUri",
            "places.rating",
            "places.userRatingCount",
            "places.primaryType",
            "places.googleMapsUri",
            "nextPageToken",
        )
    )
    API_PAGE_SIZE = 20
    API_MAX_RESULTS = 30

    def __init__(
        self,
        browser_manager=None,
        access_mode="web",
        api_key=None,
        http_post=None,
        max_results=None,
    ):
        super().__init__(browser_manager)

        access_mode = str(access_mode).strip().lower()
        if access_mode not in {"web", "api"}:
            raise ValueError("access_mode must be 'web' or 'api'.")

        if access_mode == "web" and api_key is not None:
            raise ValueError(
                "Google Maps API key is only accepted in API mode."
            )

        self.access_mode = access_mode
        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("GOOGLE_MAPS_API_KEY")
        )
        self.http_post = http_post or self._http_post
        self.max_results = (
            self.API_MAX_RESULTS
            if max_results is None
            else min(max_results, self.API_MAX_RESULTS)
        )

        if not isinstance(self.max_results, int):
            raise TypeError("max_results must be an integer.")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

        self.search_keyword = None
        self.search_location = None
        self.search_url = None
        self._api_businesses = []

    def _require_api_key(self):
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError(
                "Google Maps API key is required in API mode. "
                "Set GOOGLE_MAPS_API_KEY or pass api_key explicitly."
            )

    def _http_post(self, url, headers, body):
        request = Request(
            url,
            headers=headers,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            method="POST",
        )

        try:
            with urlopen(request, timeout=30) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            try:
                response_body = error.read().decode("utf-8")
            except Exception:
                response_body = ""
            raise GoogleMapsAPIError(
                error.code,
                f"Google Maps Places API request failed with HTTP "
                f"{error.code}: {response_body}",
            ) from error
        except URLError as error:
            raise GoogleMapsAPIError(
                None,
                f"Google Maps Places API connection failed: {error.reason}",
            ) from error

    @staticmethod
    def _map_api_place(place, query, location):
        display_name = place.get("displayName") or {}
        coordinates = place.get("location") or {}

        return {
            "name": display_name.get("text"),
            "category": place.get("primaryType"),
            "address": place.get("formattedAddress"),
            "phone": (
                place.get("nationalPhoneNumber")
                or place.get("internationalPhoneNumber")
            ),
            "website": place.get("websiteUri"),
            "instagram": None,
            "rating": place.get("rating"),
            "reviews_count": place.get("userRatingCount"),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "source": "google_maps",
            "source_id": place.get("id"),
            "source_url": place.get("googleMapsUri"),
            "google_maps_url": place.get("googleMapsUri"),
            "search_keyword": query,
            "city": location,
        }

    def _search_api(self, query, location):
        self._require_api_key()
        self.set_state(ScraperState.SEARCHING)

        search_query = f"{query} {location}".strip()
        self.search_keyword = query
        self.search_location = location
        businesses = []
        page_token = None

        try:
            while len(businesses) < self.max_results:
                body = {
                    "textQuery": search_query,
                    "pageSize": min(
                        self.API_PAGE_SIZE,
                        self.max_results - len(businesses),
                    ),
                }
                if page_token:
                    body["pageToken"] = page_token

                status_code, response_body = self.http_post(
                    self.PLACES_API_URL,
                    {
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": self.api_key,
                        "X-Goog-FieldMask": self.PLACES_FIELD_MASK,
                    },
                    body,
                )

                if not 200 <= status_code < 300:
                    raise GoogleMapsAPIError(
                        status_code,
                        f"Google Maps Places API returned HTTP "
                        f"{status_code}.",
                    )

                try:
                    response = json.loads(response_body)
                except json.JSONDecodeError as error:
                    raise GoogleMapsAPIError(
                        status_code,
                        "Google Maps Places API returned invalid JSON.",
                    ) from error

                for place in response.get("places") or []:
                    businesses.append(
                        self._map_api_place(
                            place,
                            query,
                            location,
                        )
                    )
                    if len(businesses) >= self.max_results:
                        break

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            self._api_businesses = businesses[: self.max_results]
            self.set_state(ScraperState.COMPLETED)
            return self._api_businesses

        except Exception:
            self.set_state(ScraperState.FAILED)
            logger.exception(
                "Google Maps API search failed | query=%s | location=%s",
                query,
                location,
            )
            raise

    def search(self, query, location):
        if self.access_mode == "api":
            return self._search_api(query, location)

        search_query = f"{query} {location}".strip()
        encoded_query = quote_plus(search_query)
        url = f"{self.BASE_SEARCH_URL}?api=1&query={encoded_query}"
        self.search_url = url

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

    def _extract_source_id(self, google_maps_url):
        if not google_maps_url:
            return None

        source_id_match = re.search(
            r'!1s([^!]+)',
            google_maps_url,
        )

        if not source_id_match:
            return None

        return source_id_match.group(1)

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

    def _restore_search_page(self):
        if not self.page or not self.search_url:
            return False
        try:
            current_url = self.page.url or ""
            if not isinstance(current_url, str):
                return True
            if current_url.startswith(self.BASE_SEARCH_URL):
                self.page.locator('div[role="feed"]').wait_for(
                    state="visible",
                    timeout=10000,
                )
                return True

            self.page.goto(
                self.search_url,
                wait_until="domcontentloaded",
                timeout=20000,
            )
            self.page.locator('div[role="feed"]').wait_for(
                state="visible",
                timeout=20000,
            )
            return True
        except Exception:
            logger.exception("Google Maps search page recovery failed")
            return False

    def _extract_business_details(self, card):
        """Open a result card and extract fields from its loaded place panel."""
        try:
            card.scroll_into_view_if_needed()
            card.click(timeout=10000)

            # The place panel is loaded asynchronously after the click.
            self.page.wait_for_url(
                "**/maps/place/**",
                timeout=15000,
            )

            detail_heading = self.page.locator(
                'h1[class*="DUwDvf"]'
            ).first

            if detail_heading.count() == 0:
                detail_heading = self.page.locator(
                    '[role="main"] h1'
                ).first

            detail_heading.wait_for(
                state="visible",
                timeout=15000,
            )

            # Address is a reliable signal that the detail panel has
            # finished rendering its contact fields.
            address_locator = self.page.locator(
                'button[data-item-id="address"]'
            ).first

            if address_locator.count() > 0:
                try:
                    address_locator.wait_for(
                        state="visible",
                        timeout=5000,
                    )
                except Exception:
                    pass

            self.page.wait_for_timeout(800)

            def extract_phone():
                selectors = (
                    'button[data-item-id^="phone:tel:"]',
                    'button[data-item-id^="phone:"]',
                    'a[href^="tel:"]',
                )

                for selector in selectors:
                    locator = self.page.locator(selector).first

                    if locator.count() == 0:
                        continue

                    values = (
                        locator.get_attribute("aria-label"),
                        locator.get_attribute("href"),
                        locator.inner_text(),
                        locator.get_attribute("data-item-id"),
                    )

                    for value in values:
                        if not isinstance(value, str) or not value:
                            continue

                        # Preserve Google's human-readable phone formatting
                        # when the value comes from aria-label/visible text.
                        if value.startswith(("+98", "0098")):
                            digits = re.sub(r"\D", "", value)
                            expected_digits = 12 if value.startswith("+98") else 14
                            if len(digits) == expected_digits:
                                return value.strip()

                        phone_match = re.search(
                            r'(\+98[\s\-()]*\d{2,3}[\s\-()]*\d{7,8}|'
                            r'0098[\s\-()]*\d{2,3}[\s\-()]*\d{7,8}|'
                            r'09\d{9}|0\d{2,3}[\s\-()]*\d{7,8})',
                            value,
                        )

                        if phone_match:
                            return phone_match.group(0).strip()

                        if value.startswith("tel:"):
                            return value[4:].strip()

                # Google Maps can render the phone as plain visible
                # text without a stable phone-specific attribute.
                for selector in ('[role="main"]', 'body'):
                    try:
                        text = self.page.locator(selector).inner_text()
                    except Exception:
                        continue

                    if not isinstance(text, str):
                        continue

                    phone_match = re.search(
                        r'(\+98[\s\-()]*\d{2,3}[\s\-()]*\d{7,8}|'
                        r'0098[\s\-()]*\d{2,3}[\s\-()]*\d{7,8}|'
                        r'09\d{9}|0\d{2,3}[\s\-()]*\d{7,8})',
                        text,
                    )

                    if phone_match:
                        return phone_match.group(0).strip()

                return None

            phone = extract_phone()

            website = None
            website_locator = self.page.locator(
                'a[data-item-id="authority"]'
            ).first

            if website_locator.count() > 0:
                website = website_locator.get_attribute("href")

            address = None
            if address_locator.count() > 0:
                address = address_locator.inner_text().strip() or None

            name = detail_heading.inner_text().strip()

            result = {
                "name": name or None,
                "address": address,
                "phone": phone,
                "website": website,
            }

            # Restore the search route explicitly instead of repeatedly using
            # browser history. This is more stable during long extraction runs.
            if not self._restore_search_page():
                raise RuntimeError("Google Maps search page could not be restored.")

            return result

        except Exception as error:
            self._restore_search_page()
            logger.debug(
                "Google Maps detail extraction failed | error=%s",
                error,
            )
            return {}

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
        # Detail Panel (Google Maps Web)
        # ----------------------------------------

        details = self._extract_business_details(card)

        if details.get("name"):
            name = details["name"]

        if details.get("address"):
            address = details["address"]

        if details.get("phone"):
            phone = details["phone"]

        if details.get("website"):
            website = details["website"]

        # ----------------------------------------
        # Source ID
        # ----------------------------------------

        source_id = self._extract_source_id(
            google_maps_url
        )

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

            try:
                results_container = self._get_results_container()
            except Exception:
                if not self._restore_search_page():
                    raise
                results_container = self._get_results_container()

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
        if self.access_mode == "api":
            return list(self._api_businesses)

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