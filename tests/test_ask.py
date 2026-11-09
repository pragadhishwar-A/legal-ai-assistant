import pytest
from ask import ask_question


@pytest.mark.integration
def test_ask_returns_expected_shape():
    """Needs Ollama running and a document already ingested."""
    result = ask_question("What is this document about?")
    assert "answer" in result
    assert "sources" in result
    assert "confidence" in result
    assert result["confidence"] in ("high", "medium", "low", "none")