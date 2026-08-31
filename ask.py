# ask.py
# This script answers a question using only the content of the
# previously-ingested document.

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma


def ask_question(question, collection_name="legal_docs"):
    """
    Searches the stored document for relevant text, then asks the
    AI model to answer the question using only that text.
    """

    # STEP A: Reconnect to the same ChromaDB database we created
    # in ingest.py. We must use the SAME embedding model here as we
    # did during ingestion, or the search results will be meaningless.
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    # STEP B: Search for the most relevant chunks to this question.
    # k=4 means "give me the 4 most relevant chunks."
    results = vectorstore.similarity_search(question, k=4)

    if not results:
        return "I couldn't find any relevant information in the uploaded document."

    # STEP C: Combine the retrieved chunks into one block of context text.
    context = "\n\n".join(chunk.page_content for chunk in results)

    # STEP D: Build the prompt. This is the instruction we send to the
    # AI model. Notice we explicitly tell it to answer ONLY from the
    # context — this is the key line that prevents made-up answers.
    prompt = f"""You are a legal assistant. Answer the question using
ONLY the context below, which was extracted from the user's uploaded
document. If the answer is not contained in the context, say clearly
that the document does not appear to address this — do not guess.

Context:
{context}

Question: {question}

Answer:"""

    # STEP E: Send the prompt to the AI model and get a response.
    llm = OllamaLLM(model="llama3.2")
    answer = llm.invoke(prompt)

    return answer


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"your question here\"")
    else:
        question = " ".join(sys.argv[1:])
        print(ask_question(question))