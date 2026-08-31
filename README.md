# Legal AI Assistant (RAG + LLM)

A local, privacy-first AI assistant that answers questions about legal documents using **Retrieval-Augmented Generation (RAG)**. Upload a PDF (a contract, agreement, or any legal document) and ask questions about it in plain English — answers are grounded strictly in the document's own content, not the model's general knowledge, reducing hallucination.

Runs entirely on your own machine using free, open-source tools — no API keys, no per-message costs, no data leaving your computer.

## How It Works

1. **Ingest**: A PDF is loaded, split into overlapping text chunks, converted into vector embeddings, and stored in a local vector database (ChromaDB).
2. **Retrieve**: When you ask a question, it's embedded the same way, and the most semantically similar chunks are retrieved from the database.
3. **Generate**: Those retrieved chunks are passed to a local LLM as context, with an explicit instruction to answer only from that context — and to say so plainly if the document doesn't cover the question.

```
PDF Upload → Text Splitting → Embeddings → ChromaDB (storage)
                                                ↓
User Question → Embedding → Similarity Search → Retrieved Chunks
                                                ↓
                                    LLM (grounded answer generation)
                                                ↓
                                          Answer returned to user
```

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Backend | Flask | Serves the web app and API endpoints |
| Orchestration | LangChain | Connects document loading, chunking, embeddings, and retrieval |
| Vector store | ChromaDB | Stores and searches document embeddings |
| LLM inference | Ollama (`llama3.2`) | Generates answers locally, no API cost |
| Embeddings | Ollama (`nomic-embed-text`) | Converts text into searchable vectors |
| PDF parsing | PyPDF | Extracts text from uploaded PDFs |
| Frontend | HTML / CSS / JavaScript | Simple upload + chat interface |

## Features

- Upload a legal PDF and query its contents conversationally
- Retrieval-augmented answers grounded in the actual document text
- Fully local — no cloud API keys or internet dependency for inference
- Minimal, readable codebase intended for learning RAG fundamentals

## Getting Started

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Ollama](https://ollama.com/download) installed and running

### Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/legal-ai-assistant.git
cd legal-ai-assistant

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Pull the required Ollama models
ollama pull llama3.2
ollama pull nomic-embed-text

# Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser, upload a PDF, and start asking questions.

## Project Structure

```
legal-ai-assistant/
├── app.py              # Flask app: routes for upload and chat
├── ingest.py            # Document loading, chunking, embedding, storage
├── ask.py               # Retrieval + grounded answer generation
├── templates/
│   └── index.html        # Frontend upload/chat UI
├── uploads/              # Uploaded PDFs (not committed)
├── chroma_db/            # Vector database storage (not committed)
├── requirements.txt
└── README.md
```

## Known Limitations

- Single-document store: uploading a new PDF replaces the previous one (no multi-document or multi-user support yet)
- No authentication — intended for local, single-user use
- Answer quality and speed depend on your machine's hardware, since inference runs locally

## Roadmap / Future Improvements

- [ ] Multi-document support with per-document collections
- [ ] User authentication and per-user document isolation
- [ ] Clause extraction and document drafting features
- [ ] Deployment guide for cloud hosting

## Why This Project

Built as a hands-on exploration of Retrieval-Augmented Generation — specifically how grounding LLM responses in retrieved document context reduces hallucination compared to relying on a model's parametric knowledge alone, an approach especially valuable in domains like legal document analysis where factual accuracy matters.

## License

MIT — feel free to use, learn from, or build on this project.
