# tests/test_ingest.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingest import ingest_document


def test_ingest_creates_chunks(tmp_path):
    """A real PDF should be split into at least one chunk without error."""
    # NOTE: replace this with a path to a small real test PDF you commit
    # to your repo under tests/fixtures/sample.pdf
    sample_pdf = os.path.join(os.path.dirname(__file__), "fixtures", "sample.pdf")
    vectorstore = ingest_document(sample_pdf, collection_name="test_collection")
    assert vectorstore is not None