from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    KLM_DIR,
    VIJAI_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# ============================================================
# HELPERS
# ============================================================

def read_markdown_files(directory: Path, company: str):

    documents = []

    for file_path in directory.glob("*.md"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "text": text,
            "source": file_path.name,
            "company": company,
        })

    return documents


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


# ============================================================
# MAIN INGESTION
# ============================================================

def ingest():

    print("Loading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Recreate collection to avoid stale data
    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "VijAI sales simulator knowledge base"
        }
    )

    all_documents = []

    all_documents.extend(
        read_markdown_files(
            KLM_DIR,
            "klm"
        )
    )

    all_documents.extend(
        read_markdown_files(
            VIJAI_DIR,
            "vijai"
        )
    )

    ids = []
    texts = []
    metadatas = []

    counter = 0

    for document in all_documents:

        chunks = chunk_text(
            document["text"]
        )

        for chunk in chunks:

            ids.append(
                f"chunk_{counter}"
            )

            texts.append(chunk)

            metadatas.append({
                "company": document["company"],
                "source": document["source"],
            })

            counter += 1

    print(
        f"Creating embeddings for {len(texts)} chunks..."
    )

    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("====================================")
    print("RAG ingestion completed")
    print(f"Documents/chunks: {len(texts)}")
    print(f"Database: {CHROMA_DIR}")
    print("====================================")


if __name__ == "__main__":
    ingest()