from datetime import datetime, timezone

from core.cleaner import BusinessCleaner
from core.deduplicator import Deduplicator
from core.models import Business, ScrapeRun


class ScrapePipeline:
    """
    Coordinates the scraping workflow:

    Scraper
        ↓
    Cleaner
        ↓
    Deduplicator
        ↓
    Database
        ↓
    ScrapeRun statistics
    """

    def __init__(
        self,
        scraper,
        session_factory,
        cleaner=None,
        deduplicator=None,
    ):
        self.scraper = scraper
        self.session_factory = session_factory

        self.cleaner = cleaner or BusinessCleaner()
        self.deduplicator = (
            deduplicator or Deduplicator()
        )

    def run(self, query, location):
        session = self.session_factory()

        scrape_run = ScrapeRun(
            source="google_maps",
            city=location,
            keyword=query,
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
        )

        session.add(scrape_run)
        session.commit()

        try:
            self.scraper.search(
                query=query,
                location=location,
            )

            businesses = self.scraper.scrape()

            scrape_run.total_found = len(businesses)

            existing_businesses = (
                session.query(Business).all()
            )

            existing_dicts = [
                self._business_to_dict(business)
                for business in existing_businesses
            ]

            for raw_business in businesses:
                try:
                    cleaned_business = self.cleaner.clean(
                        raw_business
                    )

                    duplicate = (
                        self.deduplicator.find_duplicate(
                            cleaned_business,
                            existing_dicts,
                        )
                    )

                    if duplicate is None:
                        business = Business(
                            **self._filter_business_fields(
                                cleaned_business
                            )
                        )

                        session.add(business)
                        session.flush()

                        existing_dicts.append(
                            self._business_to_dict(
                                business
                            )
                        )

                        scrape_run.total_new += 1

                    else:
                        existing_model = (
                            self._find_model_by_dict(
                                existing_businesses,
                                duplicate,
                            )
                        )

                        if existing_model is None:
                            scrape_run.total_errors += 1
                            continue

                        changed = self._update_business(
                            existing_model,
                            cleaned_business,
                        )

                        if changed:
                            scrape_run.total_updated += 1
                        else:
                            scrape_run.total_duplicates += 1

                except Exception:
                    scrape_run.total_errors += 1

            scrape_run.status = "COMPLETED"
            scrape_run.finished_at = datetime.now(timezone.utc)

            session.commit()

            return {
                "run_id": scrape_run.id,
                "status": scrape_run.status,
                "total_found": scrape_run.total_found,
                "total_new": scrape_run.total_new,
                "total_updated": scrape_run.total_updated,
                "total_duplicates": (
                    scrape_run.total_duplicates
                ),
                "total_errors": scrape_run.total_errors,
            }

        except Exception as error:
            session.rollback()

            scrape_run = session.get(
                ScrapeRun,
                scrape_run.id,
            )

            scrape_run.status = "FAILED"
            scrape_run.finished_at = datetime.now(timezone.utc)
            scrape_run.error_message = str(error)
            scrape_run.total_errors += 1

            session.commit()

            raise

        finally:
            session.close()

    def _filter_business_fields(self, business):
        allowed_fields = {
            "name",
            "category",
            "address",
            "city",
            "phone",
            "website",
            "instagram",
            "rating",
            "reviews_count",
            "latitude",
            "longitude",
            "google_maps_url",
            "source",
            "source_id",
            "search_keyword",
            "scraped_at",
            "source_url",
        }

        return {
            key: value
            for key, value in business.items()
            if key in allowed_fields
        }

    def _business_to_dict(self, business):
        fields = [
            "name",
            "category",
            "address",
            "city",
            "phone",
            "website",
            "instagram",
            "rating",
            "reviews_count",
            "latitude",
            "longitude",
            "google_maps_url",
            "source",
            "source_id",
            "search_keyword",
            "source_url",
        ]

        return {
            field: getattr(business, field)
            for field in fields
        }

    def _find_model_by_dict(
        self,
        models,
        target_dict,
    ):
        for model in models:
            if (
                self._business_to_dict(model)
                == target_dict
            ):
                return model

        return None

    def _update_business(
        self,
        business_model,
        cleaned_business,
    ):
        changed = False

        fields = self._filter_business_fields(
            cleaned_business
        )

        ignored_fields = {
            "source",
            "source_id",
            "scraped_at",
            "source_url",
            "search_keyword",
        }

        for field, value in fields.items():
            if field in ignored_fields:
                continue

            if value is None:
                continue

            old_value = getattr(
                business_model,
                field,
            )

            if old_value != value:
                setattr(
                    business_model,
                    field,
                    value,
                )
                changed = True

        return changed