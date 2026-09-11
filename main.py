from browser.manager import BrowserManager
from config import HEADLESS, GOOGLE_MAPS_URL, PAGE_TIMEOUT


def main():
    browser = BrowserManager(headless=HEADLESS)

    try:
        print("Starting browser...")

        page = browser.start()

        print("Opening Google Maps...")

        page.set_default_timeout(PAGE_TIMEOUT)
        page.goto(
            GOOGLE_MAPS_URL,
            wait_until="domcontentloaded"
        )

        print("Google Maps opened successfully.")
        print(f"Title: {page.title()}")

        input("\nPress Enter to close the browser...")

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        print("Closing browser...")
        browser.close()
        print("Browser closed.")


if __name__ == "__main__":
    main()