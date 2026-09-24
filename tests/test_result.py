import pytest

from core.result import ScrapeResult


def test_scrape_result_accepts_valid_data():
    result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza", "fast food"),
        run_id=1,
        total_found=100,
        total_new=80,
        total_updated=10,
        total_duplicates=8,
        total_errors=2,
    )

    assert result.status == "COMPLETED"
    assert result.source == "google_maps"
    assert result.location == "Mashhad"
    assert result.keywords == ("pizza", "fast food")
    assert result.run_id == 1
    assert result.total_found == 100
    assert result.total_new == 80
    assert result.total_updated == 10
    assert result.total_duplicates == 8
    assert result.total_errors == 2
    assert result.error_message is None


def test_scrape_result_normalizes_string_values():
    result = ScrapeResult(
        status="  COMPLETED  ",
        source=" google_maps ",
        location=" Mashhad ",
        keywords=(" pizza ", "  fast food"),
        run_id=1,
    )

    assert result.status == "COMPLETED"
    assert result.source == "google_maps"
    assert result.location == "Mashhad"
    assert result.keywords == ("pizza", "fast food")


def test_scrape_result_accepts_list_keywords():
    result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="Mashhad",
        keywords=["pizza", "fast food"],
        run_id=1,
    )

    assert result.keywords == ("pizza", "fast food")


def test_scrape_result_is_immutable():
    result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        run_id=1,
    )

    with pytest.raises(AttributeError):
        result.status = "FAILED"

    with pytest.raises(AttributeError):
        result.run_id = 99
        

@pytest.mark.parametrize(
    "field,value",
    [
        ("total_found", -1),
        ("total_new", -1),
        ("total_updated", -1),
        ("total_duplicates", -1),
        ("total_errors", -1),
    ],
)
def test_scrape_result_rejects_negative_counters(field, value):
    kwargs = {
        "status": "COMPLETED",
        "source": "google_maps",
        "location": "Mashhad",
        "keywords": ("pizza",),
        "run_id": 1,
        field: value,
    }

    with pytest.raises(ValueError, match=f"{field} cannot be negative"):
        ScrapeResult(**kwargs)


@pytest.mark.parametrize(
    "field",
    [
        "total_found",
        "total_new",
        "total_updated",
        "total_duplicates",
        "total_errors",
    ],
)
def test_scrape_result_rejects_non_integer_counters(field):
    kwargs = {
        "status": "COMPLETED",
        "source": "google_maps",
        "location": "Mashhad",
        "keywords": ("pizza",),
        "run_id": 1,
        field: "10",
    }

    with pytest.raises(TypeError, match=f"{field} must be an integer"):
        ScrapeResult(**kwargs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", ""),
        ("source", ""),
        ("location", ""),
    ],
)
def test_scrape_result_rejects_empty_required_strings(field, value):
    kwargs = {
        "status": "COMPLETED",
        "source": "google_maps",
        "location": "Mashhad",
        "keywords": ("pizza",),
        "run_id": 1,
        field: value,
    }

    with pytest.raises(ValueError):
        ScrapeResult(**kwargs)


def test_scrape_result_rejects_empty_keywords():
    with pytest.raises(ValueError, match="keywords cannot be empty"):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords=(),
            run_id=1,
        )


def test_scrape_result_rejects_non_sequence_keywords():
    with pytest.raises(TypeError, match="keywords must be a sequence"):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords="pizza",
            run_id=1,
        )


def test_scrape_result_rejects_non_string_keyword():
    with pytest.raises(TypeError, match="each keyword must be a string"):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords=("pizza", 123),
            run_id=1,
        )


def test_scrape_result_rejects_empty_keyword():
    with pytest.raises(
        ValueError,
        match="keywords cannot contain empty values",
    ):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords=("pizza", ""),
            run_id=1,
        )


def test_scrape_result_normalizes_error_message():
    result = ScrapeResult(
        status="FAILED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        error_message="  Browser failed  ",
        run_id=1,
    )

    assert result.error_message == "Browser failed"


def test_scrape_result_converts_blank_error_message_to_none():
    result = ScrapeResult(
        status="FAILED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        error_message="   ",
        run_id=1,
    )

    assert result.error_message is None


def test_scrape_result_rejects_invalid_error_message():
    with pytest.raises(
        TypeError,
        match="error_message must be a string or None",
    ):
        ScrapeResult(
            status="FAILED",
            source="google_maps",
            location="Mashhad",
            keywords=("pizza",),
            error_message=123,
            run_id=1,
        )


def test_scrape_result_accepts_failed_status_with_error_message():
    result = ScrapeResult(
        status="FAILED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        total_errors=1,
        error_message="Browser failed",
        run_id=1,
    )

    assert result.status == "FAILED"
    assert result.total_errors == 1
    assert result.error_message == "Browser failed"


@pytest.mark.parametrize(
    "run_id",
    [0, -1],
)
def test_scrape_result_rejects_invalid_run_id(run_id):
    with pytest.raises(
        ValueError,
        match="run_id must be greater than zero",
    ):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords=("pizza",),
            run_id=run_id,
        )


def test_scrape_result_rejects_non_integer_run_id():
    with pytest.raises(
        TypeError,
        match="run_id must be an integer",
    ):
        ScrapeResult(
            status="COMPLETED",
            source="google_maps",
            location="Mashhad",
            keywords=("pizza",),
            run_id="1",
        )





