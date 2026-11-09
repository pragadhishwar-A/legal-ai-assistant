import pytest
from langchain_core.documents import Document

import config
import ingest


class FakeChroma:
    deleted = False
    stored_docs = None

    def __init__(self, **kw):
        pass

    def delete_collection(self):
        FakeChroma.deleted = True

    @classmethod
    def from_documents(cls, documents, embedding, collection_name, persist_directory):
        cls.stored_docs = documents
        return cls()


class FakeLoader:
    def __init__(self, path):
        pass

    def load(self):
        text = "lorem ipsum dolor " * 200  # about 3600 chars
        return [Document(page_content=text, metadata={"page": 0, "source": "x.pdf"})]


@pytest.fixture(autouse=True)
def backends(monkeypatch):
    FakeChroma.deleted = False
    FakeChroma.stored_docs = None
    monkeypatch.setattr(ingest, "PyPDFLoader", FakeLoader)
    monkeypatch.setattr(ingest, "OllamaEmbeddings", lambda **kw: object())
    monkeypatch.setattr(ingest, "Chroma", FakeChroma)


def test_ingest_splits_into_bounded_chunks():
    store = ingest.ingest_document("whatever.pdf", collection_name="t")
    assert store is not None
    chunks = FakeChroma.stored_docs
    assert len(chunks) > 1
    assert all(len(c.page_content) <= config.CHUNK_SIZE for c in chunks)


def test_ingest_preserves_page_metadata():
    ingest.ingest_document("whatever.pdf", collection_name="t")
    assert all(c.metadata["page"] == 0 for c in FakeChroma.stored_docs)


def test_ingest_clears_previous_collection_first():
    ingest.ingest_document("whatever.pdf", collection_name="t")
    assert FakeChroma.deleted is True