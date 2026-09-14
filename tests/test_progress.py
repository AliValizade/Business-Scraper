from utils.progress import ProgressReporter, ProgressSnapshot


def test_progress_starts_with_zero_values():
    reporter = ProgressReporter()

    snapshot = reporter.get_snapshot()

    assert isinstance(snapshot, ProgressSnapshot)
    assert snapshot.total == 0
    assert snapshot.processed == 0
    assert snapshot.new == 0
    assert snapshot.updated == 0
    assert snapshot.duplicates == 0
    assert snapshot.errors == 0


def test_progress_start_sets_total():
    reporter = ProgressReporter()

    reporter.start(total=100)

    snapshot = reporter.get_snapshot()

    assert snapshot.total == 100
    assert snapshot.processed == 0


def test_progress_update_changes_values():
    reporter = ProgressReporter()

    reporter.start(total=100)

    reporter.update(
        processed=20,
        new=15,
        updated=3,
        duplicates=1,
        errors=1,
    )

    snapshot = reporter.get_snapshot()

    assert snapshot.processed == 20
    assert snapshot.new == 15
    assert snapshot.updated == 3
    assert snapshot.duplicates == 1
    assert snapshot.errors == 1


def test_progress_increment_methods():
    reporter = ProgressReporter()

    reporter.start(total=10)

    reporter.increment_processed()
    reporter.increment_new()
    reporter.increment_updated()
    reporter.increment_duplicates()
    reporter.increment_errors()

    snapshot = reporter.get_snapshot()

    assert snapshot.processed == 1
    assert snapshot.new == 1
    assert snapshot.updated == 1
    assert snapshot.duplicates == 1
    assert snapshot.errors == 1


def test_progress_percentage():
    reporter = ProgressReporter()

    reporter.start(total=200)
    reporter.update(processed=50)

    assert reporter.get_percentage() == 25.0


def test_progress_percentage_with_zero_total():
    reporter = ProgressReporter()

    reporter.start(total=0)

    assert reporter.get_percentage() == 0.0


def test_get_snapshot_returns_independent_object():
    reporter = ProgressReporter()

    reporter.start(total=10)
    reporter.increment_processed()

    snapshot = reporter.get_snapshot()

    reporter.increment_processed()

    assert snapshot.processed == 1
    assert reporter.get_snapshot().processed == 2


def test_progress_supports_keyword_context():
    reporter = ProgressReporter()

    reporter.start(
        total=50,
        current_keyword="فست فود",
        keyword_index=1,
        total_keywords=3,
    )

    snapshot = reporter.get_snapshot()

    assert snapshot.total == 50
    assert snapshot.current_keyword == "فست فود"
    assert snapshot.keyword_index == 1
    assert snapshot.total_keywords == 3


def test_progress_can_switch_keyword():
    reporter = ProgressReporter()

    reporter.start(
        total=20,
        current_keyword="فست فود",
        keyword_index=1,
        total_keywords=3,
    )

    reporter.set_keyword(
        keyword="پیتزا",
        keyword_index=2,
        total_keywords=3,
    )

    snapshot = reporter.get_snapshot()

    assert snapshot.current_keyword == "پیتزا"
    assert snapshot.keyword_index == 2
    assert snapshot.total_keywords == 3

