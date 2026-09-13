from core.deduplicator import Deduplicator


def test_duplicate_by_source_and_source_id():
    deduplicator = Deduplicator()

    existing = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": None,
        "source": "google_maps",
        "source_id": "ChIJ123",
    }

    new_business = {
        "name": "Different Name",
        "address": "Different Address",
        "phone": None,
        "source": "google_maps",
        "source_id": "ChIJ123",
    }

    duplicate = deduplicator.find_duplicate(
        new_business,
        [existing],
    )

    assert duplicate is existing


def test_same_source_id_from_different_source_can_match_by_name_and_address():
    deduplicator = Deduplicator()

    existing = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": None,
        "source": "google_maps",
        "source_id": "123",
    }

    new_business = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": None,
        "source": "neshan",
        "source_id": "123",
    }

    assert deduplicator.is_duplicate(
        new_business,
        [existing],
    )


def test_duplicate_by_phone():
    deduplicator = Deduplicator()

    existing = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": "+989123456789",
        "source": "google_maps",
        "source_id": None,
    }

    new_business = {
        "name": "Sara Pizza",
        "address": "Different Address",
        "phone": "+989123456789",
        "source": "google_maps",
        "source_id": None,
    }

    duplicate = deduplicator.find_duplicate(
        new_business,
        [existing],
    )

    assert duplicate is existing


def test_duplicate_by_name_and_address():
    deduplicator = Deduplicator()

    existing = {
        "name": "پیتزا سارا",
        "address": "مشهد بلوار سجاد",
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    new_business = {
        "name": "پیتزا سارا",
        "address": "مشهد بلوار سجاد",
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    assert deduplicator.is_duplicate(
        new_business,
        [existing],
    )


def test_same_name_without_address_is_not_duplicate():
    deduplicator = Deduplicator()

    existing = {
        "name": "Pizza Sara",
        "address": None,
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    new_business = {
        "name": "Pizza Sara",
        "address": None,
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    assert not deduplicator.is_duplicate(
        new_business,
        [existing],
    )


def test_same_phone_is_not_duplicate_when_phone_is_missing():
    deduplicator = Deduplicator()

    existing = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    new_business = {
        "name": "Pizza Sara",
        "address": "Mashhad",
        "phone": None,
        "source": "google_maps",
        "source_id": None,
    }

    assert deduplicator.is_duplicate(
        new_business,
        [existing],
    )


def test_deduplicate_keeps_first_occurrence():
    deduplicator = Deduplicator()

    businesses = [
        {
            "name": "Pizza Sara",
            "address": "Mashhad",
            "phone": "+989123456789",
            "source": "google_maps",
            "source_id": None,
        },
        {
            "name": "Sara Pizza",
            "address": "Different Address",
            "phone": "+989123456789",
            "source": "google_maps",
            "source_id": None,
        },
        {
            "name": "Ace Burger",
            "address": "Mashhad",
            "phone": "+989111111111",
            "source": "google_maps",
            "source_id": None,
        },
    ]

    unique_businesses, duplicates = (
        deduplicator.deduplicate(businesses)
    )

    assert len(unique_businesses) == 2
    assert len(duplicates) == 1

    assert unique_businesses[0]["name"] == "Pizza Sara"
    assert unique_businesses[1]["name"] == "Ace Burger"
    assert duplicates[0]["name"] == "Sara Pizza"


def test_matching_priority_source_id_before_phone():
    deduplicator = Deduplicator()

    source_id_match = {
        "name": "Business A",
        "address": "Address A",
        "phone": "+989111111111",
        "source": "google_maps",
        "source_id": "ID-A",
    }

    phone_match = {
        "name": "Business B",
        "address": "Address B",
        "phone": "+989222222222",
        "source": "google_maps",
        "source_id": None,
    }

    new_business = {
        "name": "New Business",
        "address": "New Address",
        "phone": "+989222222222",
        "source": "google_maps",
        "source_id": "ID-A",
    }

    duplicate = deduplicator.find_duplicate(
        new_business,
        [
            phone_match,
            source_id_match,
        ],
    )

    assert duplicate is source_id_match