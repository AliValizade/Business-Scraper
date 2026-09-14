from dataclasses import dataclass


@dataclass
class ProgressSnapshot:
    total: int = 0
    processed: int = 0
    new: int = 0
    updated: int = 0
    duplicates: int = 0
    errors: int = 0

    current_keyword: str | None = None
    keyword_index: int = 0
    total_keywords: int = 0


class ProgressReporter:
    def __init__(self):
        self.snapshot = ProgressSnapshot()

    def start(
        self,
        total=0,
        current_keyword=None,
        keyword_index=0,
        total_keywords=0,
    ):
        self.snapshot = ProgressSnapshot(
            total=total,
            current_keyword=current_keyword,
            keyword_index=keyword_index,
            total_keywords=total_keywords,
        )

    def update(
        self,
        total=None,
        processed=None,
        new=None,
        updated=None,
        duplicates=None,
        errors=None,
        current_keyword=None,
        keyword_index=None,
        total_keywords=None,
    ):
        if total is not None:
            self.snapshot.total = total

        if processed is not None:
            self.snapshot.processed = processed

        if new is not None:
            self.snapshot.new = new

        if updated is not None:
            self.snapshot.updated = updated

        if duplicates is not None:
            self.snapshot.duplicates = duplicates

        if errors is not None:
            self.snapshot.errors = errors

        if current_keyword is not None:
            self.snapshot.current_keyword = current_keyword

        if keyword_index is not None:
            self.snapshot.keyword_index = keyword_index

        if total_keywords is not None:
            self.snapshot.total_keywords = total_keywords

    def set_keyword(
        self,
        keyword,
        keyword_index,
        total_keywords,
    ):
        self.snapshot.current_keyword = keyword
        self.snapshot.keyword_index = keyword_index
        self.snapshot.total_keywords = total_keywords

    def increment_processed(self):
        self.snapshot.processed += 1

    def increment_new(self):
        self.snapshot.new += 1

    def increment_updated(self):
        self.snapshot.updated += 1

    def increment_duplicates(self):
        self.snapshot.duplicates += 1

    def increment_errors(self):
        self.snapshot.errors += 1

    def get_snapshot(self):
        return ProgressSnapshot(
            total=self.snapshot.total,
            processed=self.snapshot.processed,
            new=self.snapshot.new,
            updated=self.snapshot.updated,
            duplicates=self.snapshot.duplicates,
            errors=self.snapshot.errors,
            current_keyword=self.snapshot.current_keyword,
            keyword_index=self.snapshot.keyword_index,
            total_keywords=self.snapshot.total_keywords,
        )

    def get_percentage(self):
        if self.snapshot.total <= 0:
            return 0.0

        return (
            self.snapshot.processed
            / self.snapshot.total
            * 100
        )



    