# ask.py

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
import config


def ask_question(question, collection_name="legal_docs"):
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    results = vectorstore.similarity_search_with_score(question, k=config.RETRIEVAL_K)

    if not results:
        return {
            "answer": "I couldn't find any relevant information in the uploaded document.",
            "sources": [],
            "confidence": "none",
        }

    # Separate the chunks and their similarity scores
    chunks = [r[0] for r in results]
    scores = [r[1] for r in results]

    context = "\n\n".join(chunk.page_content for chunk in chunks)

    prompt = f"""You are a legal assistant. Answer the question using
ONLY the context below, which was extracted from the user's uploaded
document. If the answer is not contained in the context, say clearly
that the document does not appear to address this — do not guess.

Context:
{context}

Question: {question}

Answer:"""

    llm = OllamaLLM(model=config.LLM_MODEL)
    answer = llm.invoke(prompt)

    # Build a list of unique source pages, in order of relevance
        # Build a list of unique source pages, sorted in ascending page order
    sources = []
    seen_pages = set()
    for chunk in chunks:
        page = chunk.metadata.get("page", "unknown")
        source_file = chunk.metadata.get("source", "document")
        if page not in seen_pages:
            sources.append({"page": page + 1 if isinstance(page, int) else page, "file": source_file})
            seen_pages.add(page)

    # Sort numerically by page number. Non-numeric pages (e.g. "unknown")
    # are pushed to the end instead of breaking the sort.
    sources.sort(key=lambda s: s["page"] if isinstance(s["page"], int) else float("inf"))

    # Chroma's distance score: lower = more similar. We convert it to a
    # simple high/medium/low label so the frontend doesn't need to
    # understand the raw math.
    best_score = min(scores) if scores else 1.0
    if best_score < 0.5:
        confidence = "high"
    elif best_score < 0.8:
        confidence = "medium"
    else:
        confidence = "low"

    return {"answer": answer, "sources": sources, "confidence": confidence}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"your question here\"")
    else:
        question = " ".join(sys.argv[1:])
        result = ask_question(question)
        print(result["answer"])
        print("Sources:", result["sources"])
        print("Confidence:", result["confidence"])