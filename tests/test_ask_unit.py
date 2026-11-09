import pytest
from langchain_core.documents import Document

import ask


class FakeStore:
    def __init__(self, results):
        self._results = results

    def similarity_search_with_score(self, question, k):
        return self._results


class FakeLLM:
    def __init__(self):
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return "stub answer"


@pytest.fixture
def backends(monkeypatch):
    def apply(results):
        llm = FakeLLM()
        monkeypatch.setattr(ask, "OllamaEmbeddings", lambda **kw: object())
        monkeypatch.setattr(ask, "Chroma", lambda **kw: FakeStore(results))
        monkeypatch.setattr(ask, "OllamaLLM", lambda **kw: llm)
        return llm
    return apply


def doc(text="clause text", page=0, source="a.pdf"):
    meta = {"source": source}
    if page is not None:
        meta["page"] = page
    return Document(page_content=text, metadata=meta)


def test_no_results_returns_none_without_calling_llm(backends):
    llm = backends([])
    result = ask.ask_question("anything")
    assert result["confidence"] == "none"
    assert result["sources"] == []
    assert llm.prompts == []


def test_sources_deduplicated_sorted_and_one_indexed(backends):
    results = [(doc(page=4), 0.2), (doc(page=0), 0.3), (doc(page=4), 0.4), (doc(page=1), 0.5)]
    backends(results)
    pages = [s["page"] for s in ask.ask_question("q")["sources"]]
    assert pages == [1, 2, 5]


def test_missing_page_sorts_last(backends):
    backends([(doc(page=None), 0.2), (doc(page=2), 0.3)])
    pages = [s["page"] for s in ask.ask_question("q")["sources"]]
    assert pages == [3, "unknown"]


@pytest.mark.parametrize("score,label", [
    (0.49, "high"), (0.50, "medium"), (0.79, "medium"), (0.80, "low"),
])
def test_confidence_thresholds(backends, score, label):
    backends([(doc(), score)])
    assert ask.ask_question("q")["confidence"] == label


def test_confidence_uses_best_score(backends):
    backends([(doc(), 0.9), (doc(page=1), 0.3)])
    assert ask.ask_question("q")["confidence"] == "high"


def test_prompt_contains_context_and_question(backends):
    llm = backends([(doc(text="The tenant shall pay rent monthly."), 0.2)])
    ask.ask_question("When is rent due?")
    assert "The tenant shall pay rent monthly." in llm.prompts[0]
    assert "When is rent due?" in llm.prompts[0]