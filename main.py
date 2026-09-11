from browser.manager import BrowserManager
from config import (
    HEADLESS,
    PAGE_TIMEOUT,
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

        input("\nPress Enter to close the browser...")

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        print("\nClosing browser...")
        browser.close()
        print("Browser closed.")


if __name__ == "__main__":
    main()