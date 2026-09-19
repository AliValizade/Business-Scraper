from types import SimpleNamespace
from unittest.mock import Mock
import pytest

from cli.commands import run_scrape_command, format_scrape_result
from cli.parser import create_parser

from core.result import ScrapeResult

import main


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

    expected_result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=(
            "پیتزا",
            "رستوران",
        ),
    )

    application.run = lambda **kwargs: expected_result

    args = SimpleNamespace(
        source="google_maps",
        location="مشهد",
        keywords=[
            "پیتزا",
            "رستوران",
        ],
        max_results=None,
    )

    result = run_scrape_command(
        args,
        application,
    )

    assert result is expected_result


def test_run_scrape_command_passes_keywords_unchanged():
    calls = []

    class FakeApplication:
        def run(self, **kwargs):
            calls.append(kwargs)

            return ScrapeResult(
                status="COMPLETED",
                source="google_maps",
                location="مشهد",
                keywords=(
                    "پیتزا",
                    "فست فود",
                ),
            )

    args = SimpleNamespace(
        source="google_maps",
        location="مشهد",
        keywords=[
            "پیتزا",
            "فست فود",
        ],
        max_results=None,
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
            "max_results": None,
        }
    ]


def test_format_scrape_result():
    result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=(
            "پیتزا",
            "رستوران",
        ),
        total_found=100,
        total_new=80,
        total_updated=10,
        total_duplicates=10,
        total_errors=2,
    )

    formatted = format_scrape_result(
        result
    )

    assert formatted == (
        "Status: COMPLETED\n"
        "Found: 100\n"
        "New: 80\n"
        "Updated: 10\n"
        "Duplicates: 10\n"
        "Errors: 2"
    )


def test_format_scrape_result_uses_defaults():
    result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=("پیتزا",),
    )

    formatted = format_scrape_result(
        result
    )

    assert formatted == (
        "Status: COMPLETED\n"
        "Found: 0\n"
        "New: 0\n"
        "Updated: 0\n"
        "Duplicates: 0\n"
        "Errors: 0"
    )

   
def test_main_prints_formatted_scrape_result(
    monkeypatch,
    capsys,
):
    fake_application = Mock()

    expected_result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        total_found=10,
        total_new=8,
        total_updated=1,
        total_duplicates=1,
        total_errors=0,
    )

    fake_application.run.return_value = expected_result

    monkeypatch.setattr(
        main,
        "create_cli_application",
        lambda source: fake_application,
    )

    result = main.main(
        [
            "scrape",
            "--source",
            "google_maps",
            "--location",
            "Mashhad",
            "--keyword",
            "pizza",
        ]
    )

    captured = capsys.readouterr()

    assert "Status: COMPLETED" in captured.out
    assert "Found: 10" in captured.out
    assert "New: 8" in captured.out
    assert "Updated: 1" in captured.out
    assert "Duplicates: 1" in captured.out
    assert "Errors: 0" in captured.out

    assert result is expected_result

