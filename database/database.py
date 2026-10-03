from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "business_scraper.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


Base = declarative_base()


def init_db():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    Base.metadata.create_all(
        bind=engine
    )

    inspector = inspect(engine)
    if "scrape_runs" in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns("scrape_runs")
        }
        if "access_mode" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE scrape_runs "
                        "ADD COLUMN access_mode VARCHAR(20) "
                        "NOT NULL DEFAULT 'web'"
                    )
                )