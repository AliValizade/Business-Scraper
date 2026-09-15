from pathlib import Path

import pytest

from exporters.base import BaseExporter


def test_base_exporter_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseExporter()


def test_base_exporter_requires_export_implementation():
    class IncompleteExporter(BaseExporter):
        pass

    with pytest.raises(TypeError):
        IncompleteExporter()


def test_concrete_exporter_can_implement_export():
    class FakeExporter(BaseExporter):
        def export(self, data, output_path):
            return Path(output_path)

    exporter = FakeExporter()

    result = exporter.export(
        data=[{"name": "Test Business"}],
        output_path="output/test.csv",
    )

    assert result == Path("output/test.csv")