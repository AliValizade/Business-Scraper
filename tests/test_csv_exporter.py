import csv

from exporters.csv_exporter import CSVExporter


def test_csv_exporter_creates_file(tmp_path):
    output_path = tmp_path / "businesses.csv"

    data = [
        {
            "name": "Pizza Sara",
            "city": "Mashhad",
            "phone": "09121234567",
        },
        {
            "name": "Fast Food Center",
            "city": "Mashhad",
            "phone": "09129876543",
        },
    ]

    exporter = CSVExporter()

    result = exporter.export(data, output_path)

    assert result == output_path
    assert output_path.exists()


def test_csv_exporter_writes_header_and_rows(tmp_path):
    output_path = tmp_path / "businesses.csv"

    data = [
        {
            "name": "Pizza Sara",
            "city": "Mashhad",
            "phone": "09121234567",
        },
        {
            "name": "Fast Food Center",
            "city": "Mashhad",
            "phone": "09129876543",
        },
    ]

    CSVExporter().export(data, output_path)

    with output_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert rows == [
        {
            "name": "Pizza Sara",
            "city": "Mashhad",
            "phone": "09121234567",
        },
        {
            "name": "Fast Food Center",
            "city": "Mashhad",
            "phone": "09129876543",
        },
    ]


def test_csv_exporter_supports_string_output_path(tmp_path):
    output_path = tmp_path / "businesses.csv"

    data = [
        {
            "name": "Pizza Sara",
        },
    ]

    result = CSVExporter().export(
        data,
        str(output_path),
    )

    assert result == output_path
    assert output_path.exists()


def test_csv_exporter_creates_parent_directory(tmp_path):
    output_path = (
        tmp_path
        / "exports"
        / "businesses.csv"
    )

    data = [
        {
            "name": "Pizza Sara",
        },
    ]

    CSVExporter().export(data, output_path)

    assert output_path.exists()


def test_csv_exporter_handles_empty_data(tmp_path):
    output_path = tmp_path / "empty.csv"

    result = CSVExporter().export([], output_path)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(
        encoding="utf-8-sig",
    )

    assert content == ""