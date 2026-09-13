from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    instagram: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reviews_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    google_maps_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    search_keyword: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_businesses_source_source_id",
            "source",
            "source_id",
        ),
        Index(
            "ix_businesses_name",
            "name",
        ),
        Index(
            "ix_businesses_phone",
            "phone",
        ),
    )


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    keyword: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    total_found: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_new: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_duplicates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_errors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_scrape_runs_source",
            "source",
        ),
        Index(
            "ix_scrape_runs_started_at",
            "started_at",
        ),
    )