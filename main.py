from browser.manager import BrowserManager
from config import (
    HEADLESS,
    MAX_RESULTS,
    MAX_SCROLL_ATTEMPTS,
    PAGE_TIMEOUT,
    SCROLL_WAIT_TIME,
    SEARCH_LOCATION,
    SEARCH_QUERY,
)
from scrapers.google_maps import GoogleMapsScraper


def main():
    browser = BrowserManager(headless=HEADLESS)
    scraper = GoogleMapsScraper(browser)

    try:
        print("Starting browser...")

        browser.start()
        browser.page.set_default_timeout(PAGE_TIMEOUT)

        print("Searching Google Maps...")
        print(f"Query: {SEARCH_QUERY}")
        print(f"Location: {SEARCH_LOCATION}")

        scraper.search(
            query=SEARCH_QUERY,
            location=SEARCH_LOCATION
        )

        print("\nGoogle Maps search opened successfully.")
        print(f"Title: {scraper.page.title()}")
        print(f"URL: {scraper.page.url}")

        scraper.inspect_results()

        businesses = scraper.scroll_results(
            max_results=MAX_RESULTS,
            max_scroll_attempts=MAX_SCROLL_ATTEMPTS,
            wait_time=SCROLL_WAIT_TIME,
        )

        print("\n--- Extracted Businesses ---")

        for index, business in enumerate(
            businesses,
            start=1
        ):
            print(
                f"\n[{index}] "
                f"{business['name']}"
            )

            print(
                f"    Address: "
                f"{business['address']}"
            )

            print(
                f"    Rating: "
                f"{business['rating']}"
            )

            print(
                f"    Reviews: "
                f"{business['reviews_count']}"
            )

        input("\nPress Enter to close the browser...")

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        print("\nClosing browser...")
        browser.close()
        print("Browser closed.")


if __name__ == "__main__":
    main()