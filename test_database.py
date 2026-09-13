from database.database import init_db
from core.models import Business, ScrapeRun


def main():
    init_db()

    print("Database initialized successfully.")
    print(f"Business table: {Business.__tablename__}")
    print(f"ScrapeRun table: {ScrapeRun.__tablename__}")


if __name__ == "__main__":
    main()