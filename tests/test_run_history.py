from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application import Application
from cli.commands import (
    format_run,
    format_runs,
    run_get_run_command,
    run_list_runs_command,
)
from cli.parser import create_parser
from core.errors import RunNotFoundError
from core.models import Base, ScrapeRun


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    yield factory

    engine.dispose()


@pytest.fixture
def application(session_factory):
    return Application(
        pipeline=object(),
        session_factory=session_factory,
    )


def add_run(session_factory, **overrides):
    defaults = {
        "source": "google_maps",
        "city": "Mashhad",
        "keyword": "pizza",
        "status": "COMPLETED",
        "total_found": 10,
        "total_new": 8,
        "total_updated": 1,
        "total_duplicates": 1,
        "total_errors": 0,
    }
    defaults.update(overrides)

    session = session_factory()
    try:
        run = ScrapeRun(**defaults)
        session.add(run)
        session.commit()
        session.refresh(run)
        return run.id
    finally:
        session.close()


def test_application_get_run_returns_plain_dict(
    application,
    session_factory,
):
    run_id = add_run(
        session_factory,
        error_message=None,
    )

    result = application.get_run(run_id)

    assert isinstance(result, dict)
    assert result["id"] == run_id
    assert result["source"] == "google_maps"
    assert result["city"] == "Mashhad"
    assert result["keyword"] == "pizza"
    assert result["status"] == "COMPLETED"
    assert result["total_found"] == 10


def test_application_get_run_raises_for_missing_run(
    application,
):
    with pytest.raises(
        RunNotFoundError,
        match="Scrape run with id 999 was not found",
    ):
        application.get_run(999)


def test_application_get_run_closes_session(
    monkeypatch,
):
    class FakeQuery:
        def filter(self, expression):
            return self

        def one_or_none(self):
            return None

    class FakeSession:
        def __init__(self):
            self.closed = False

        def query(self, model):
            return FakeQuery()

        def close(self):
            self.closed = True

    session = FakeSession()

    application = Application(
        pipeline=object(),
        session_factory=lambda: session,
    )

    with pytest.raises(RunNotFoundError):
        application.get_run(1)

    assert session.closed is True


def test_application_list_runs_orders_by_started_at_then_id(
    application,
    session_factory,
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    older_id = add_run(
        session_factory,
        started_at=now - timedelta(minutes=10),
    )
    newer_id = add_run(
        session_factory,
        started_at=now,
    )
    same_time_lower_id = add_run(
        session_factory,
        started_at=now,
    )

    runs = application.list_runs()

    assert [run["id"] for run in runs[:3]] == [
        same_time_lower_id,
        newer_id,
        older_id,
    ]


def test_application_list_runs_applies_limit(
    application,
    session_factory,
):
    for index in range(3):
        add_run(
            session_factory,
            started_at=datetime(
                2026,
                1,
                index + 1,
            ),
        )

    runs = application.list_runs(limit=2)

    assert len(runs) == 2
    assert runs[0]["started_at"] > runs[1]["started_at"]


def test_application_list_runs_returns_empty_list(
    application,
):
    assert application.list_runs() == []


@pytest.mark.parametrize(
    "value, expected_exception",
    [
        (True, TypeError),
        ("1", TypeError),
        (0, ValueError),
        (-1, ValueError),
    ],
)
def test_application_get_run_validates_run_id(
    application,
    value,
    expected_exception,
):
    with pytest.raises(expected_exception):
        application.get_run(value)


@pytest.mark.parametrize(
    "value, expected_exception",
    [
        (True, TypeError),
        ("10", TypeError),
        (0, ValueError),
        (-1, ValueError),
    ],
)
def test_application_list_runs_validates_limit(
    application,
    value,
    expected_exception,
):
    with pytest.raises(expected_exception):
        application.list_runs(value)


def test_parser_creates_runs_command():
    parser = create_parser()

    args = parser.parse_args(
        ["runs", "--limit", "5"]
    )

    assert args.command == "runs"
    assert args.limit == 5


def test_parser_runs_uses_default_limit():
    parser = create_parser()

    args = parser.parse_args(["runs"])

    assert args.command == "runs"
    assert args.limit == 20


def test_parser_creates_run_command():
    parser = create_parser()

    args = parser.parse_args(
        ["run", "42"]
    )

    assert args.command == "run"
    assert args.run_id == 42


def test_run_history_commands_delegate_to_application():
    application = type(
        "FakeApplication",
        (),
        {
            "list_runs": lambda self, limit: [
                {"id": limit}
            ],
            "get_run": lambda self, run_id: {
                "id": run_id
            },
        },
    )()

    runs = run_list_runs_command(
        type("Args", (), {"limit": 7})(),
        application,
    )
    run = run_get_run_command(
        type("Args", (), {"run_id": 42})(),
        application,
    )

    assert runs == [{"id": 7}]
    assert run == {"id": 42}


def test_format_run():
    run = {
        "id": 42,
        "source": "google_maps",
        "city": "Mashhad",
        "keyword": "pizza",
        "started_at": "2026-09-25 10:00:00",
        "finished_at": "2026-09-25 10:01:00",
        "status": "COMPLETED",
        "total_found": 10,
        "total_new": 8,
        "total_updated": 1,
        "total_duplicates": 1,
        "total_errors": 0,
        "error_message": None,
    }

    assert format_run(run) == (
        "ID: 42\n"
        "Source: google_maps\n"
        "City: Mashhad\n"
        "Keyword: pizza\n"
        "Started: 2026-09-25 10:00:00\n"
        "Finished: 2026-09-25 10:01:00\n"
        "Status: COMPLETED\n"
        "Found: 10\n"
        "New: 8\n"
        "Updated: 1\n"
        "Duplicates: 1\n"
        "Errors: 0\n"
        "Error: None"
    )


def test_format_runs_handles_empty_history():
    assert format_runs([]) == "No scrape runs found."


def test_format_runs_formats_multiple_runs():
    runs = [
        {
            "id": 2,
            "source": "google_maps",
            "city": "Mashhad",
            "keyword": "pizza",
            "started_at": "a",
            "finished_at": "b",
            "status": "COMPLETED",
            "total_found": 1,
            "total_new": 1,
            "total_updated": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "error_message": None,
        },
        {
            "id": 1,
            "source": "google_maps",
            "city": "Tehran",
            "keyword": "restaurant",
            "started_at": "c",
            "finished_at": "d",
            "status": "FAILED",
            "total_found": 0,
            "total_new": 0,
            "total_updated": 0,
            "total_duplicates": 0,
            "total_errors": 1,
            "error_message": "boom",
        },
    ]

    formatted = format_runs(runs)

    assert "ID: 2" in formatted
    assert "ID: 1" in formatted
    assert "Error: boom" in formatted
    assert "\n\n" in formatted
