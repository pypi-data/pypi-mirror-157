import json
from pathlib import Path

import pytest
from pymultirole_plugins.v1.schema import Document

from pyprocessors_rf_consolidate.rf_consolidate import (
    RFConsolidateProcessor,
    RFConsolidateParameters,
)


def test_model():
    model = RFConsolidateProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == RFConsolidateParameters


# Arrange
@pytest.fixture
def original_doc():
    testdir = Path(__file__).parent
    source = Path(testdir, "data/testfuzzybuild2206-document-test.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
        return original_doc


def test_rf_consolidate_acro(original_doc):
    doc = original_doc.copy(deep=True)
    processor = RFConsolidateProcessor()
    parameters = RFConsolidateParameters()
    docs = processor.process([doc], parameters)
    conso: Document = docs[0]
    assert len(conso.annotations) < len(original_doc.annotations)
