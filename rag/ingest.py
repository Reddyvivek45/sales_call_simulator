from pathlib import Path
import pickle
import sys

import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

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
# MAKE simulator/ IMPORTABLE
# ============================================================

SIMULATOR_DIR = (
    Path(__file__).resolve().parent.parent
    / "sales_web" / "simulator"
)

sys.path.append(str(SIMULATOR_DIR))

from topics import TOPIC_SEQUENCE 


# ============================================================
# BM25 STORAGE
# ============================================================

BM25_DIR = Path(CHROMA_DIR) / "bm25"

BM25_INDEX_FILE = BM25_DIR / "bm25_index.pkl"

BM25_DOCUMENTS_FILE = BM25_DIR / "bm25_documents.pkl"


# ============================================================
# HELPERS
# ============================================================

def read_markdown_files(
    directory: Path,
    company: str,
):

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


def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks
# ============================================================
# TOPIC INFERENCE
# ============================================================

def infer_topic(chunk_text):

    text_lower = chunk_text.lower()

    best_topic_id = "general"
    best_hits = 0

    for topic in TOPIC_SEQUENCE:

        hits = sum(
            1 for keyword in topic["keywords"]
            if keyword in text_lower
        )

        if hits > best_hits:

            best_hits = hits
            best_topic_id = topic["id"]

    return best_topic_id


# ============================================================
# BM25 TOKENIZER
# ============================================================

def tokenize(text):

    return text.lower().split()


# ============================================================
# MAIN INGESTION
# ============================================================

def ingest():

    print()
    print("=" * 60)
    print("STARTING RAG INGESTION")
    print("=" * 60)


    # ========================================================
    # LOAD EMBEDDING MODEL
    # ========================================================

    print()
    print("Loading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )


    # ========================================================
    # CONNECT TO CHROMADB
    # ========================================================

    print()
    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


    # ========================================================
    # DELETE OLD COLLECTION
    # ========================================================

    try:

        client.delete_collection(
            COLLECTION_NAME
        )

        print(
            f"Deleted existing collection: "
            f"{COLLECTION_NAME}"
        )

    except Exception:

        print(
            "No existing Chroma collection found."
        )


    # ========================================================
    # CREATE COLLECTION
    # ========================================================

    collection = client.create_collection(

        name=COLLECTION_NAME,

        metadata={
            "description":
                "VijAI sales simulator knowledge base"
        },

        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )


    # ========================================================
    # READ ALL MARKDOWN FILES
    # ========================================================

    all_documents = []

    all_documents.extend(
        read_markdown_files(
            KLM_DIR,
            "klm",
        )
    )

    all_documents.extend(
        read_markdown_files(
            VIJAI_DIR,
            "vijai",
        )
    )


    print()
    print(
        f"Markdown documents found: "
        f"{len(all_documents)}"
    )


    # ========================================================
    # CREATE CHUNKS
    # ========================================================

    ids = []

    texts = []

    metadatas = []

    counter = 0


    for document in all_documents:

        chunks = chunk_text(
            document["text"]
        )


        for chunk in chunks:

            chunk_id = (
                f"chunk_{counter}"
            )


            ids.append(
                chunk_id
            )


            texts.append(
                chunk
            )


            metadatas.append({

                "company":
                    document["company"],

                "source":
                    document["source"],
                "topic":
                    infer_topic(chunk),

            })


            counter += 1


    print(
        f"Total chunks created: "
        f"{len(texts)}"
    )


    # ========================================================
    # CREATE SEMANTIC EMBEDDINGS
    # ========================================================

    print()
    print(
        f"Creating embeddings for "
        f"{len(texts)} chunks..."
    )


    embeddings = embedding_model.encode(

        texts,

        normalize_embeddings=True,

        show_progress_bar=True,
    ).tolist()


    # ========================================================
    # STORE IN CHROMADB
    # ========================================================

    collection.add(

        ids=ids,

        documents=texts,

        embeddings=embeddings,

        metadatas=metadatas,
    )


    print(
        "ChromaDB ingestion completed."
    )


    # ========================================================
    # CREATE BM25 INDEX
    # ========================================================

    print()
    print("Creating BM25 index...")


    tokenized_documents = [

        tokenize(text)

        for text in texts

    ]


    bm25 = BM25Okapi(
        tokenized_documents
    )


    # ========================================================
    # CREATE BM25 DIRECTORY
    # ========================================================

    BM25_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ========================================================
    # SAVE BM25 INDEX
    # ========================================================

    with open(
        BM25_INDEX_FILE,
        "wb",
    ) as file:

        pickle.dump(
            bm25,
            file,
        )


    # ========================================================
    # SAVE DOCUMENT INFORMATION
    # ========================================================

    bm25_documents = {

        "ids": ids,

        "texts": texts,

        "metadatas": metadatas,

    }


    with open(
        BM25_DOCUMENTS_FILE,
        "wb",
    ) as file:

        pickle.dump(
            bm25_documents,
            file,
        )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print()
    print("=" * 60)
    print("RAG INGESTION COMPLETED")
    print("=" * 60)

    print(
        f"Documents : {len(all_documents)}"
    )

    print(
        f"Chunks    : {len(texts)}"
    )

    print(
        f"ChromaDB  : {CHROMA_DIR}"
    )

    print(
        f"BM25      : {BM25_INDEX_FILE}"
    )

    print("=" * 60)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    ingest()