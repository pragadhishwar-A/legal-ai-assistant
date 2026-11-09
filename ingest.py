# ingest.py
# This script takes a PDF file and prepares it for question-answering.

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import config
# in ingest_document:
embeddings_for_reset = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
)
embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)

def ingest_document(pdf_path, collection_name="legal_docs"):
    """
    Reads a PDF, splits it into chunks, and stores it in ChromaDB
    so it can be searched later.
    """

    # STEP 0: Clear out any previously stored document first.
    # Since this is a single-document assistant, we don't want old
    # and new documents mixed together in the same search results.
    embeddings_for_reset = OllamaEmbeddings(model="nomic-embed-text")
    try:
        existing_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings_for_reset,
            persist_directory="./chroma_db",
        )
        existing_store.delete_collection()
        print("Cleared previous document from the database.")
    except Exception:
        # If there was nothing to clear (e.g. first run ever), that's fine.
        pass

    # STEP A: Load the PDF and extract its raw text.
    # PyPDFLoader reads the file page by page.
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} page(s) from {pdf_path}")

    # STEP B: Split the text into smaller overlapping chunks.
    # We do this because AI models work best with focused, bite-sized
    # pieces of text rather than one giant block. The "overlap" means
    # each chunk shares a little text with the next one, so we don't
    # accidentally cut a sentence or clause in half.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      # roughly 800 characters per chunk
        chunk_overlap=150,   # 150 characters shared with the next chunk
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunk(s)")

    # STEP C: Convert each chunk into a "meaning vector" using the
    # embedding model, and store all of them in ChromaDB.
    # This is what makes it possible to later search "by meaning"
    # rather than just by exact keyword match.
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="./chroma_db",  # saves to disk, not just memory
    )

    print("Document successfully ingested and stored.")
    return vectorstore


if __name__ == "__main__":
    # This block only runs if you execute this file directly
    # (not if it's imported by another file, like app.py later).
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <path_to_pdf>")
    else:
        ingest_document(sys.argv[1])