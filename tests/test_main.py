from types import SimpleNamespace
from unittest.mock import Mock

from core.result import ScrapeResult

import main


def test_create_cli_application_uses_requested_source(
    monkeypatch,
):
    fake_application = Mock()
    captured = {}

    def fake_create_application(
        session_factory,
        browser_manager,
        source,
    ):
        captured["session_factory"] = (
            session_factory
        )
        captured["browser_manager"] = (
            browser_manager
        )
        captured["source"] = source

        return fake_application

    monkeypatch.setattr(
        main,
        "create_application",
        fake_create_application,
    )

    fake_browser_manager = object()

    monkeypatch.setattr(
        main,
        "BrowserManager",
        lambda: fake_browser_manager,
    )

    fake_session_local = object()

    monkeypatch.setattr(
        main,
        "SessionLocal",
        fake_session_local,
    )

    result = main.create_cli_application(
        source="google_maps",
    )

    assert result is fake_application

    assert (
        captured["session_factory"]
        is fake_session_local
    )

    assert (
        captured["browser_manager"]
        is fake_browser_manager
    )

    assert (
        captured["source"]
        == "google_maps"
    )


def test_main_runs_scrape_command(
    monkeypatch,
):
    fake_application = Mock()

    fake_result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=("پیتزا",),
        total_found=10,
    )

    fake_application.run.return_value = (
        fake_result
    )

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
            "مشهد",
            "--keyword",
            "پیتزا",
        ]
    )

    assert result is fake_result

    fake_application.run.assert_called_once_with(
        location="مشهد",
        keywords=["پیتزا"],
        max_results=None,
    )


def test_main_supports_multiple_keywords(
    monkeypatch,
):
    fake_application = Mock()

    fake_application.run.return_value = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=(
            "پیتزا",
            "فست فود",
            "رستوران",
        ),
    )

    monkeypatch.setattr(
        main,
        "create_cli_application",
        lambda source: fake_application,
    )

    main.main(
        [
            "scrape",
            "--source",
            "google_maps",
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

    fake_application.run.assert_called_once_with(
        location="مشهد",
        keywords=[
            "پیتزا",
            "فست فود",
            "رستوران",
        ],
        max_results=None,
    )


def test_main_passes_source_to_application_composition(
    monkeypatch,
):
    fake_application = Mock()

    captured = {}

    def fake_create_cli_application(
        source,
    ):
        captured["source"] = source
        return fake_application

    monkeypatch.setattr(
        main,
        "create_cli_application",
        fake_create_cli_application,
    )

    fake_application.run.return_value = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=("پیتزا",),
    )

    main.main(
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

    assert (
        captured["source"]
        == "google_maps"
    )