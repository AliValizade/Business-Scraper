import pytest

from cli.commands import (
    format_run_businesses,
    run_get_run_businesses_command,
)
from cli.parser import create_parser
from core.errors import RunNotFoundError


class FakeApplication:
    def __init__(self, businesses=None, error=None):
        self.businesses = businesses or []
        self.error = error

    def get_run_businesses(self, run_id):
        if self.error:
            raise self.error

        return self.businesses


def test_parser_supports_run_businesses_flag():
    parser = create_parser()

    args = parser.parse_args([
        "run",
        "42",
        "--businesses",
    ])

    assert args.command == "run"
    assert args.run_id == 42
    assert args.businesses is True


def test_existing_run_command_defaults_to_without_businesses():
    parser = create_parser()

    args = parser.parse_args([
        "run",
        "42",
    ])

    assert args.command == "run"
    assert args.run_id == 42
    assert args.businesses is False


def test_run_businesses_command_uses_application_service():
    application = FakeApplication(
        businesses=[
            {
                "id": 1,
                "name": "Pizza Sara",
            },
        ]
    )
    args = type("Args", (), {"run_id": 42})()

    result = run_get_run_businesses_command(
        args,
        application,
    )

    assert result == application.businesses


def test_format_run_businesses():
    businesses = [
        {
            "id": 1,
            "name": "Pizza Sara",
            "category": "Restaurant",
            "city": "Mashhad",
            "address": "Mashhad",
            "phone": "+989123456789",
            "rating": 4.2,
            "reviews_count": 120,
            "source": "google_maps",
            "google_maps_url": "https://www.google.com/maps/place/test",
        },
    ]

    output = format_run_businesses(businesses)

    assert "ID: 1" in output
    assert "Name: Pizza Sara" in output
    assert "Category: Restaurant" in output
    assert "City: Mashhad" in output
    assert "Address: Mashhad" in output
    assert "Phone: +989123456789" in output
    assert "Rating: 4.2" in output
    assert "Reviews: 120" in output
    assert "Source: google_maps" in output
    assert "URL: https://www.google.com/maps/place/test" in output


def test_format_run_businesses_empty():
    assert (
        format_run_businesses([])
        == "No businesses found for this run."
    )


def test_run_businesses_preserves_run_not_found_error():
    application = FakeApplication(
        error=RunNotFoundError("Run 999 not found.")
    )
    args = type("Args", (), {"run_id": 999})()

    with pytest.raises(RunNotFoundError):
        run_get_run_businesses_command(
            args,
            application,
        )


def test_cli_startup_initializes_database(monkeypatch):
    from main import main

    initialized = {"value": False}

    def fake_init_db():
        initialized["value"] = True

    monkeypatch.setattr("main.init_db", fake_init_db)

    with pytest.raises(SystemExit):
        main(["--help"])

    assert initialized["value"] is True
