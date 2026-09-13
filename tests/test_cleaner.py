from core.cleaner import BusinessCleaner
from utils.phone import normalize_phone
from utils.text import normalize_digits, normalize_persian_text


def test_persian_text_normalization():
    value = "  پيتزا   سارا  "

    result = normalize_persian_text(value)

    assert result == "پیتزا سارا"


def test_digit_normalization():
    assert normalize_digits("۱۲۳۴۵") == "12345"
    assert normalize_digits("١٢٣٤٥") == "12345"


def test_phone_normalization():
    assert normalize_phone("0912-345-6789") == "+989123456789"


def test_business_cleaning():
    raw_business = {
        "name": "  پيتزا   سارا  ",
        "category": " رستوران  ",
        "address": "  مشهد، بلوار   سجاد ",
        "city": " مشهد ",
        "phone": "0912-345-6789",
        "website": " https://example.com ",
        "instagram": None,
        "rating": "۴٫۲",
        "reviews_count": "۱,۲۳۴",
        "latitude": "36.315284",
        "longitude": "59.5095218",
        "google_maps_url": " https://www.google.com/maps/place/test ",
        "source": "google_maps",
        "source_id": None,
        "search_keyword": " فست   فود ",
    }

    cleaner = BusinessCleaner()
    cleaned = cleaner.clean(raw_business)

    assert cleaned["name"] == "پیتزا سارا"
    assert cleaned["category"] == "رستوران"
    assert cleaned["address"] == "مشهد، بلوار سجاد"
    assert cleaned["city"] == "مشهد"
    assert cleaned["phone"] == "+989123456789"
    assert cleaned["rating"] == 4.2
    assert cleaned["reviews_count"] == 1234
    assert cleaned["latitude"] == 36.315284
    assert cleaned["longitude"] == 59.5095218
    assert cleaned["website"] == "https://example.com"
    assert cleaned["search_keyword"] == "فست فود"


def test_invalid_rating_becomes_none():
    cleaner = BusinessCleaner()

    business = {
        "name": "Test",
        "rating": "9.7",
    }

    cleaned = cleaner.clean(business)

    assert cleaned["rating"] is None


def test_none_values_are_preserved():
    cleaner = BusinessCleaner()

    business = {
        "name": None,
        "phone": None,
        "website": None,
        "rating": None,
        "reviews_count": None,
    }

    cleaned = cleaner.clean(business)

    assert cleaned["name"] is None
    assert cleaned["phone"] is None
    assert cleaned["website"] is None
    assert cleaned["rating"] is None
    assert cleaned["reviews_count"] is None