import json

from exporters.json_exporter import JSONExporter


def test_json_exporter_creates_file(tmp_path):
    output_path = tmp_path / "businesses.json"

    data = [
        {
            "name": "Pizza Sara",
            "city": "Mashhad",
            "phone": "09121234567",
        },
    ]

    exporter = JSONExporter()

    result = exporter.export(data, output_path)

    assert result == output_path
    assert output_path.exists()


def test_json_exporter_writes_valid_json(tmp_path):
    output_path = tmp_path / "businesses.json"

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

    JSONExporter().export(data, output_path)

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        result = json.load(file)

    assert result == data


def test_json_exporter_preserves_persian_text(tmp_path):
    output_path = tmp_path / "businesses.json"

    data = [
        {
            "name": "پیتزا سارا",
            "city": "مشهد",
            "address": "بلوار سجاد",
        },
    ]

    JSONExporter().export(data, output_path)

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert "پیتزا سارا" in content
    assert "مشهد" in content
    assert "\\u067e" not in content


def test_json_exporter_supports_string_output_path(tmp_path):
    output_path = tmp_path / "businesses.json"

    data = [
        {
            "name": "Pizza Sara",
        },
    ]

    result = JSONExporter().export(
        data,
        str(output_path),
    )

    assert result == output_path
    assert output_path.exists()


def test_json_exporter_creates_parent_directory(tmp_path):
    output_path = (
        tmp_path
        / "exports"
        / "businesses.json"
    )

    data = [
        {
            "name": "Pizza Sara",
        },
    ]

    JSONExporter().export(data, output_path)

    assert output_path.exists()


def test_json_exporter_handles_empty_data(tmp_path):
    output_path = tmp_path / "empty.json"

    result = JSONExporter().export([], output_path)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert json.loads(content) == []