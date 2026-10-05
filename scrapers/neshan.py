import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import RETRY_COUNT, RETRY_DELAY
from core.states import ScraperState
from scrapers.base import BaseScraper
from utils.logger import get_logger
from utils.retry import retry


logger = get_logger(__name__)


class NeshanAPIError(RuntimeError):
    """Raised when a Neshan API request fails."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)


class NeshanScraper(BaseScraper):
    """Neshan adapter with public Web scraping as the default path.

    API access remains available as an explicit optional mode.
    """

    BASE_URL = "https://api.neshan.org"
    WEB_URL = "https://neshan.org/maps/search"
    SEARCH_PATH = "/v3/search"
    GEOCODING_PATH = "/geocoding/v1"
    POI_DETAILS_PATH = "/v1/point"
    MAX_RESULTS = 30
    DEFAULT_MODE = "web"

    SEARCH_INPUT_SELECTORS = (
        "input.AZLBjuP",
        'input[placeholder*="جستجو"]',
        'input[type="search"]',
    )
    SEARCH_TRIGGER_SELECTORS = (
        "input.f5AeHfr",
        'input[placeholder*="جستجو"]',
        'button[type="submit"]',
    )
    RESULT_SELECTORS = (
        ".nrFZBE4",
        '[class*="nrFZBE4"]',
    )
    DETAIL_NAME_SELECTORS = (
        "h1.ZzIY7hD",
        "h1",
    )
    DETAIL_CATEGORY_SELECTORS = (
        "span.qpxuHlU",
        "span",
    )
    DETAIL_RATING_SELECTORS = (
        ".qZI77s3",
        '[class*="qZI77s3"]',
    )
    DETAIL_INFO_BUTTON_SELECTORS = (
        "button.wE_mwzL",
        "button",
    )
    DETAIL_HOURS_SELECTORS = (
        "div.GiQOShA",
        '[class*="GiQOShA"]',
    )

    def __init__(
        self,
        browser_manager=None,
        api_key=None,
        http_get=None,
        max_results=None,
        access_mode="web",
        mode=None,
    ):
        super().__init__(browser_manager)

        if mode is not None:
            access_mode = mode

        access_mode = str(access_mode).strip().lower()
        if access_mode not in {"web", "api"}:
            raise ValueError("access_mode must be 'web' or 'api'.")

        self.access_mode = access_mode
        self.mode = access_mode

        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("NESHAN_API_KEY")
        )
        self.http_get = http_get or self._http_get
        self.max_results = (
            self.MAX_RESULTS
            if max_results is None
            else min(max_results, self.MAX_RESULTS)
        )

        if not isinstance(self.max_results, int):
            raise TypeError("max_results must be an integer.")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

        self.search_keyword = None
        self.search_location = None
        self._businesses = []
        self._result_cards = None
        self._detail_urls = []

    # ------------------------------------------------------------------
    # API mode (optional)
    # ------------------------------------------------------------------

    def _require_api_key(self):
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError(
                "Neshan API key is required in API mode. "
                "Set NESHAN_API_KEY or pass api_key explicitly."
            )

    def _build_url(self, path, params):
        return f"{self.BASE_URL}{path}?{urlencode(params)}"

    def _http_get(self, url):
        request = Request(
            url,
            headers={
                "Api-Key": self.api_key,
                "Accept": "application/json",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            try:
                body = error.read().decode("utf-8")
            except Exception:
                body = ""
            raise NeshanAPIError(
                error.code,
                f"Neshan API request failed with HTTP {error.code}: {body}",
            ) from error
        except URLError as error:
            raise NeshanAPIError(
                None,
                f"Neshan API connection failed: {error.reason}",
            ) from error

    def _get_json(self, path, params):
        self._require_api_key()
        status_code, body = self.http_get(
            self._build_url(path, params)
        )

        if not 200 <= status_code < 300:
            raise NeshanAPIError(
                status_code,
                f"Neshan API returned HTTP {status_code}.",
            )

        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise NeshanAPIError(
                status_code,
                "Neshan API returned invalid JSON.",
            ) from error

    @staticmethod
    def _parse_location(location):
        if not isinstance(location, dict):
            return None, None
        try:
            return float(location["latitude"]), float(location["longitude"])
        except (KeyError, TypeError, ValueError):
            return None, None

    def _geocode_location(self, location):
        response = self._get_json(
            self.GEOCODING_PATH,
            {
                "json": json.dumps(
                    {"address": str(location).strip()},
                    ensure_ascii=False,
                )
            },
        )
        items = response.get("items") or []
        if not items:
            raise ValueError(
                f"Neshan could not resolve location '{location}'."
            )

        latitude, longitude = self._parse_location(
            items[0].get("location")
        )
        if latitude is None or longitude is None:
            raise ValueError(
                f"Neshan returned an invalid location for '{location}'."
            )
        return latitude, longitude

    def _search_api(self, query, latitude, longitude):
        response = self._get_json(
            self.SEARCH_PATH,
            {
                "q": json.dumps(
                    {
                        "term": query,
                        "center": {
                            "latitude": latitude,
                            "longitude": longitude,
                        },
                    },
                    ensure_ascii=False,
                )
            },
        )
        return (response.get("items") or [])[: self.max_results]

    def _get_poi_details(self, poi_hash):
        response = self._get_json(
            self.POI_DETAILS_PATH,
            {"hash": poi_hash},
        )
        if not isinstance(response, dict):
            raise NeshanAPIError(
                200,
                "Neshan POI Details returned an invalid response.",
            )
        return response

    # ------------------------------------------------------------------
    # Web mode
    # ------------------------------------------------------------------

    def _require_page(self):
        if self.browser_manager is None:
            raise RuntimeError(
                "BrowserManager is required for Neshan web scraping."
            )

        if self.browser_manager.page is None:
            raise RuntimeError(
                "BrowserManager must be started before searching."
            )

        self.page = self.browser_manager.page
        return self.page

    @staticmethod
    def _first_visible(page, selectors):
        """Return the first selector that becomes visible.

        Neshan is a client-rendered SPA, so an element may not exist yet
        immediately after domcontentloaded. Waiting on the locator itself
        is therefore more reliable than checking count() first.
        """
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                locator.wait_for(
                    state="visible",
                    timeout=15000,
                )
                return locator
            except PlaywrightTimeoutError:
                continue
        return None

    def _open_web_map(self):
        page = self._require_page()
        retry(
            lambda: page.goto(
                "https://neshan.org/maps",
                wait_until="domcontentloaded",
            ),
            retries=RETRY_COUNT,
            delay=RETRY_DELAY,
            exceptions=(TimeoutError, PlaywrightTimeoutError),
        )
        return page

    def _fill_web_search(self, value):
        page = self._require_page()

        input_locator = None
        for selector in self.SEARCH_INPUT_SELECTORS:
            candidate = page.locator(selector).first
            try:
                candidate.wait_for(
                    state="visible",
                    timeout=15000,
                )
            except PlaywrightTimeoutError:
                continue

            # Neshan initially exposes a readonly search shell. Clicking it
            # opens/enables the real search control.
            try:
                readonly = candidate.get_attribute("readonly")
            except Exception:
                readonly = None

            if readonly is not None:
                try:
                    candidate.click()
                    candidate.wait_for(
                        state="visible",
                        timeout=5000,
                    )
                except Exception:
                    continue

            input_locator = candidate
            break

        if input_locator is None:
            raise RuntimeError("Neshan search input was not found.")

        try:
            input_locator.fill(value, timeout=5000)
        except Exception as error:
            raise RuntimeError(
                "Neshan search input was not editable."
            ) from error

        input_locator.press("Enter")

    def _wait_web_results(self):
        page = self._require_page()
        for selector in self.RESULT_SELECTORS:
            candidate = page.locator(selector)
            try:
                candidate.first.wait_for(
                    state="visible",
                    timeout=20000,
                )
                return candidate
            except PlaywrightTimeoutError:
                continue
        raise RuntimeError("Neshan search results were not loaded.")

    @staticmethod
    def _extract_map_center(url):
        if not url:
            return None, None

        match = re.search(
            r"#c(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)-",
            url,
        )
        if not match:
            return None, None

        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            return None, None

    def _resolve_web_location(self, location):
        """Resolve the requested location through Neshan Web itself.

        The resolved map center is then reused for the actual keyword search,
        avoiding a hard-coded city-coordinate table.
        """
        page = self._open_web_map()
        self._fill_web_search(str(location).strip())
        results = self._wait_web_results()

        location_text = str(location).strip()
        candidates = []
        count = min(results.count(), 20)

        for index in range(count):
            card = results.nth(index)
            try:
                text = card.inner_text(timeout=1000).strip()
            except Exception:
                continue

            if location_text and location_text in text:
                candidates.insert(0, card)
            else:
                candidates.append(card)

        if not candidates:
            raise RuntimeError(
                f"Neshan could not resolve location '{location}'."
            )

        resolved = False
        for card in candidates:
            try:
                card.scroll_into_view_if_needed()
                heading = card.locator("h2").first
                if heading.count() == 0:
                    continue

                heading.click(force=True)
                page.wait_for_timeout(800)

                latitude, longitude = self._extract_map_center(page.url)
                if latitude is None or longitude is None:
                    page.go_back(wait_until="domcontentloaded")
                    continue

                resolved = True
                break
            except Exception:
                try:
                    page.go_back(wait_until="domcontentloaded")
                except Exception:
                    pass

        if not resolved:
            raise RuntimeError(
                f"Neshan could not resolve location '{location}'."
            )

        # Re-enter the public map route while preserving the dynamically
        # resolved center. The center came from Neshan, not from our code.
        page.goto(
            f"https://neshan.org/maps#c{latitude:.6f}-{longitude:.6f}-12z-0p",
            wait_until="domcontentloaded",
        )
        self._first_visible(
            page,
            self.SEARCH_INPUT_SELECTORS,
        )
        return latitude, longitude

    def _search_web(self, query, location):
        page = self._require_page()
        self._resolve_web_location(location)

        search_query = str(query).strip()
        self._fill_web_search(search_query)

        return self._wait_web_results()


    @staticmethod
    def _extract_source_id(url):
        if not url:
            return None

        match = re.search(r"/maps/places/([^/]+)", url)
        return match.group(1) if match else None

    @staticmethod
    def _extract_coordinates(url):
        if not url:
            return None, None

        match = re.search(
            r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
            url,
        )
        if not match:
            return None, None

        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            return None, None

    @staticmethod
    def _parse_rating(text):
        if not text:
            return None, None

        normalized = (
            text.replace("۰", "0")
            .replace("۱", "1")
            .replace("۲", "2")
            .replace("۳", "3")
            .replace("۴", "4")
            .replace("۵", "5")
            .replace("۶", "6")
            .replace("۷", "7")
            .replace("۸", "8")
            .replace("۹", "9")
            .replace("٫", ".")
        )
        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*\((\d+)\)",
            normalized,
        )
        if not match:
            return None, None

        try:
            return (
                float(match.group(1).replace(",", ".")),
                int(match.group(2)),
            )
        except ValueError:
            return None, None

    def _extract_detail(self, detail_url):
        page = self._require_page()

        name_locator = self._first_visible(
            page,
            self.DETAIL_NAME_SELECTORS,
        )
        if name_locator is None:
            return None

        name = name_locator.inner_text().strip()

        category = None
        category_locator = self._first_visible(
            page,
            self.DETAIL_CATEGORY_SELECTORS,
        )
        if category_locator is not None:
            category = category_locator.inner_text().strip() or None

        rating = None
        reviews_count = None
        rating_locator = self._first_visible(
            page,
            self.DETAIL_RATING_SELECTORS,
        )
        if rating_locator is not None:
            rating, reviews_count = self._parse_rating(
                rating_locator.inner_text()
            )

        address = None
        phone = None
        website = None

        buttons = page.locator(
            self.DETAIL_INFO_BUTTON_SELECTORS[0]
        )
        count = buttons.count()

        for index in range(count):
            button = buttons.nth(index)
            text = button.inner_text().replace("\u200e", "").strip()
            image = button.locator("img").first
            src = (
                image.get_attribute("src")
                if image.count() > 0
                else ""
            )
            lower_src = (src or "").lower()

            if "pin.png" in lower_src:
                address = text or address
            elif "call.png" in lower_src or "شماره تماس" in text:
                phone = text.replace(
                    "شماره تماس:",
                    "",
                    1,
                ).strip() or phone
            elif "world.png" in lower_src:
                link = button.locator("a").first
                if link.count() > 0:
                    website = link.get_attribute("href") or website
            elif any(
                token in text
                for token in ("کوچه", "خیابان", "بلوار", "میدان")
            ):
                address = address or text

        latitude, longitude = self._extract_coordinates(
            detail_url
        )

        return {
            "name": name,
            "category": category,
            "address": address,
            "phone": phone,
            "website": website,
            "instagram": None,
            "rating": rating,
            "reviews_count": reviews_count,
            "latitude": latitude,
            "longitude": longitude,
            "source": "neshan",
            "source_id": self._extract_source_id(detail_url),
            "source_url": detail_url,
            "google_maps_url": None,
            "search_keyword": self.search_keyword,
            "city": self.search_location,
        }

    def _scrape_web(self):
        page = self._require_page()
        results = self._result_cards

        businesses = []
        seen_ids = set()
        previous_count = 0

        while len(businesses) < self.max_results:
            current_count = results.count()

            for index in range(current_count):
                if len(businesses) >= self.max_results:
                    break

                card = results.nth(index)
                try:
                    card.scroll_into_view_if_needed()
                    heading = card.locator("h2").first
                    if heading.count() == 0:
                        continue

                    heading.click(force=True)
                    page.wait_for_selector(
                        "h1.ZzIY7hD",
                        timeout=10000,
                    )

                    detail_url = page.url
                    source_id = self._extract_source_id(detail_url)

                    if source_id in seen_ids:
                        page.go_back(
                            wait_until="domcontentloaded"
                        )
                        results = page.locator(
                            self.RESULT_SELECTORS[0]
                        )
                        continue

                    business = self._extract_detail(detail_url)
                    if business and business.get("name"):
                        businesses.append(business)
                        if source_id:
                            seen_ids.add(source_id)

                except Exception:
                    logger.exception(
                        "Neshan web detail extraction failed | index=%s",
                        index,
                    )

                finally:
                    if page.url != self.WEB_URL:
                        try:
                            page.go_back(
                                wait_until="domcontentloaded"
                            )
                        except Exception:
                            logger.exception(
                                "Neshan result navigation back failed."
                            )

                    results = page.locator(
                        self.RESULT_SELECTORS[0]
                    )

            if len(businesses) >= self.max_results:
                break

            current_count = results.count()
            if current_count == previous_count:
                break

            previous_count = current_count
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)

        return businesses

    # ------------------------------------------------------------------
    # Shared adapter contract
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_instagram(social_networks):
        if not isinstance(social_networks, list):
            return None

        for network in social_networks:
            if not isinstance(network, dict):
                continue

            name = str(
                network.get("name")
                or network.get("type")
                or ""
            ).lower()

            if "instagram" in name:
                return (
                    network.get("url")
                    or network.get("value")
                    or network.get("link")
                )

        return None

    def _map_business(self, item, details=None):
        """Backward-compatible alias for the normalized API mapper."""
        return self._map_api_business(item, details=details)

    def _map_api_business(self, item, details=None):
        details = details or {}
        search_location = item.get("location") or {}
        detail_location = details.get("location") or search_location

        latitude = detail_location.get("y")
        longitude = detail_location.get("x")

        try:
            latitude = float(latitude) if latitude is not None else None
        except (TypeError, ValueError):
            latitude = None

        try:
            longitude = float(longitude) if longitude is not None else None
        except (TypeError, ValueError):
            longitude = None

        layer = details.get("layer") or {}

        return {
            "name": details.get("name") or item.get("title"),
            "category": (
                layer.get("title")
                or item.get("category")
                or item.get("type")
            ),
            "address": details.get("address") or item.get("address"),
            "phone": details.get("phoneNumber"),
            "website": details.get("website"),
            "instagram": self._extract_instagram(
                details.get("socialNetworks")
            ),
            "rating": None,
            "reviews_count": None,
            "latitude": latitude,
            "longitude": longitude,
            "source": "neshan",
            "source_id": item.get("poiHash"),
            "source_url": (
                f"{self.BASE_URL}{self.SEARCH_PATH}"
            ),
            "google_maps_url": None,
            "search_keyword": self.search_keyword,
            "city": self.search_location,
        }

    def search(self, query, location):
        self.set_state(ScraperState.SEARCHING)
        self.search_keyword = query
        self.search_location = location
        self._businesses = []

        try:
            if self.access_mode == "api":
                latitude, longitude = self._geocode_location(location)
                self.set_state(ScraperState.LOADING)
                self._businesses = self._search_api(
                    query,
                    latitude,
                    longitude,
                )
                return self._businesses

            self.set_state(ScraperState.LOADING)
            self._result_cards = self._search_web(
                query,
                location,
            )
            return self._result_cards

        except Exception:
            self.set_state(ScraperState.FAILED)
            logger.exception(
                "Neshan search failed | access_mode=%s | query=%s | location=%s",
                self.access_mode,
                query,
                location,
            )
            raise

    def scrape(self):
        if self.access_mode == "api":
            if not self._businesses:
                return []

            self.set_state(ScraperState.EXTRACTING)
            businesses = []

            for item in self._businesses[: self.max_results]:
                details = None
                poi_hash = item.get("poiHash")

                if poi_hash:
                    try:
                        details = self._get_poi_details(poi_hash)
                    except Exception as error:
                        logger.warning(
                            "Neshan POI enrichment failed | "
                            "poi_hash=%s | error=%s",
                            poi_hash,
                            error,
                        )

                businesses.append(
                    self._map_api_business(
                        item,
                        details=details,
                    )
                )

            self.set_state(ScraperState.COMPLETED)
            return businesses

        self.set_state(ScraperState.EXTRACTING)
        businesses = self._scrape_web()
        self.set_state(ScraperState.COMPLETED)

        logger.info(
            "Neshan web scraping completed | businesses=%s",
            len(businesses),
        )
        return businesses
