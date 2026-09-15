from types import SimpleNamespace

import pytest

from cli.commands import run_scrape_command
from cli.parser import create_parser


def test_parser_creates_scrape_command():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert args.command == "scrape"


def test_parser_uses_google_maps_by_default():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert args.source == "google_maps"


def test_parser_accepts_custom_source():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--source",
            "google_maps",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert args.source == "google_maps"


def test_parser_accepts_location():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert args.location == "مشهد"


def test_parser_accepts_single_keyword():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert args.keywords == ["پیتزا"]


def test_parser_accepts_multiple_keywords():
    parser = create_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--location",
            "مشهد",
            "--keyword",
            "پیتزا",
            "--keyword",
            "فست فود",
            "--keyword",
            "رستوران",
        ]
    )

    assert args.keywords == [
        "پیتزا",
        "فست فود",
        "رستوران",
    ]


def test_parser_requires_location():
    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "scrape",
                "--keyword",
                "پیتزا",
            ]
        )


def test_parser_requires_keyword():
    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "scrape",
                "--location",
                "مشهد",
            ]
        )


def test_parser_requires_command():
    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_run_scrape_command_calls_application():
    application = SimpleNamespace()

    application.run = lambda **kwargs: {
        "status": "COMPLETED",
        "location": kwargs["location"],
        "keywords": kwargs["keywords"],
    }

    args = SimpleNamespace(
        source="google_maps",
        location="مشهد",
        keywords=["پیتزا", "رستوران"],
    )

    result = run_scrape_command(
        args,
        application,
    )

    assert result == {
        "status": "COMPLETED",
        "location": "مشهد",
        "keywords": [
            "پیتزا",
            "رستوران",
        ],
    }


def test_run_scrape_command_passes_keywords_unchanged():
    calls = []

    class FakeApplication:
        def run(self, **kwargs):
            calls.append(kwargs)
            return {
                "status": "COMPLETED",
            }

    args = SimpleNamespace(
        source="google_maps",
        location="مشهد",
        keywords=[
            "پیتزا",
            "فست فود",
        ],
    )

    run_scrape_command(
        args,
        FakeApplication(),
    )

    assert calls == [
        {
            "location": "مشهد",
            "keywords": [
                "پیتزا",
                "فست فود",
            ],
        }
    ]