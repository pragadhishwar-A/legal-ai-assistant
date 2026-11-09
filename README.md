# Ledger: Local Legal Document Assistant (RAG)

![CI](https://github.com/pragadhishwar-A/legal-ai-assistant/actions/workflows/ci.yml/badge.svg)

A privacy-first assistant that answers questions about a legal PDF using **Retrieval-Augmented Generation (RAG)**. Upload a contract or agreement, ask questions in plain English, and get answers grounded in the document's own text, with page citations and a confidence label.

Everything runs on your machine with open-source tools. No API keys, no per-message costs, and no document data leaves your computer.

## How It Works

1. **Ingest:** the PDF is loaded page by page, split into overlapping chunks, embedded with `nomic-embed-text`, and stored in ChromaDB.
2. **Retrieve:** your question is embedded the same way and the most similar chunks are fetched.
3. **Generate:** the chunks are passed to a local LLM (`llama3.2`) with an instruction to answer only from that context and to say so when the document doesn't cover the question.
4. **Cite:** the response includes the source pages (ascending, 1-indexed) and a `high / medium / low / none` confidence label derived from retrieval distance.

```
PDF -> chunks -> embeddings -> ChromaDB
                                  |
question -> embedding -> similarity search -> top-k chunks
                                  |
                         llama3.2 (grounded answer)
                                  |
                   answer + page citations + confidence
```

## Features

- Upload a PDF and ask questions conversationally
- Answers grounded in retrieved document text, with page citations
- Confidence label for each answer
- Upload validation: PDF-only, file signature check, filename sanitising, configurable size limit
- Two-pane "law office ledger" interface with dark/light/auto themes, density modes, accessibility work (targeting WCAG 2.1 AA), skeleton loading, an onboarding tour and toast notifications
- Settings via environment variables
- Unit tests with mocked models, run on every push by GitHub Actions

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | Flask |
| Orchestration | LangChain |
| Vector store | ChromaDB |
| LLM | Ollama, `llama3.2` |
| Embeddings | Ollama, `nomic-embed-text` |
| PDF parsing | pypdf |
| Frontend | Vanilla HTML / CSS / JS |
| Tests / CI | pytest, GitHub Actions |

## Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### Setup

```bash
git clone https://github.com/pragadhishwar-A/legal-ai-assistant.git
cd legal-ai-assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1

pip install -r requirements.txt

ollama pull llama3.2
ollama pull nomic-embed-text

cp .env.example .env            # Windows: copy .env.example .env
python app.py
```

Open http://127.0.0.1:5000, upload a PDF, and start asking questions.

### Configuration

All settings are optional and read from `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Ollama model used for answers |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama model used for embeddings |
| `MAX_UPLOAD_MB` | `10` | Maximum PDF size |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Characters shared between chunks |
| `RETRIEVAL_K` | `4` | Chunks retrieved per question |

Set `FLASK_DEBUG=1` to enable Flask debug mode locally. It is off by default and must not be used in any shared deployment.

## Testing

```bash
pip install pytest
pytest -m "not integration"     # fast unit tests, no Ollama needed (this is what CI runs)
pytest -m integration           # needs Ollama running and a document already ingested
```

## Project Structure

```
legal-ai-assistant/
├── app.py            # Flask routes: /, /upload, /chat
├── ingest.py         # Load, chunk, embed, store
├── ask.py            # Retrieve, generate, cite, score confidence
├── config.py         # Settings loaded from .env
├── templates/        # index.html
├── static/           # CSS and JS
├── tests/            # Unit tests (mocked) and integration tests
├── .github/workflows/ci.yml
├── requirements.txt
└── pytest.ini
```

## Known Limitations

- **Single document:** uploading a new PDF replaces the previous one.
- No authentication. Intended for local, single-user use.
- Confidence labels are a heuristic based on retrieval distance and have not been calibrated against a labelled test set.
- Answer quality and speed depend on your hardware, since inference runs locally.
- Not legal advice. Always verify answers against the source document.

## Roadmap

- [ ] Multi-document support with per-document collections
- [ ] Streaming responses (Server-Sent Events)
- [ ] Conversation memory
- [ ] Docker deployment
- [ ] Structured logging
- [ ] Calibrate confidence thresholds on real documents

## License

MIT
