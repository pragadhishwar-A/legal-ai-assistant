# tests/test_ask.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ask import ask_question


def test_ask_returns_expected_shape():
    """The response should always include answer, sources, and confidence."""
    result = ask_question("What is this document about?")
    assert "answer" in result
    assert "sources" in result
    assert "confidence" in result
    assert result["confidence"] in ("high", "medium", "low", "none")