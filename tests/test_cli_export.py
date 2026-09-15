from pathlib import Path

from cli.commands import (
    format_export_result,
    run_export_command,
)


class FakeApplication:
    def __init__(self):
        self.calls = []

    def export(
        self,
        data,
        output_path,
        format_name,
    ):
        self.calls.append(
            {
                "data": data,
                "output_path": output_path,
                "format_name": format_name,
            }
        )

        return Path(output_path)


def test_run_export_command_calls_application():
    application = FakeApplication()

    args = type(
        "Args",
        (),
        {
            "output_path": "output/businesses.csv",
            "format_name": "csv",
        },
    )()

    data = [
        {"name": "Pizza Sara"},
    ]

    result = run_export_command(
        args,
        application,
        data,
    )

    assert result == Path(
        "output/businesses.csv"
    )

    assert application.calls == [
        {
            "data": data,
            "output_path": "output/businesses.csv",
            "format_name": "csv",
        }
    ]


def test_format_export_result():
    result = format_export_result(
        "output/businesses.csv",
        "csv",
    )

    assert result == (
        "Export completed successfully.\n"
        "Format: csv\n"
        "Output: output/businesses.csv"
    )