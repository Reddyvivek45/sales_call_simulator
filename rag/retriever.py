import chromadb

from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)


class Retriever:

    def __init__(self):

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_collection(
            COLLECTION_NAME
        )

    def search(self, query, top_k=TOP_K):

        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        output = []

        for i, (document, metadata) in enumerate(
            zip(documents, metadatas)
        ):

            output.append({
                "text": document,
                "company": metadata.get(
                    "company",
                    "unknown"
                ),
                "source": metadata.get(
                    "source",
                    "unknown"
                ),
                "distance": distances[i]
                if i < len(distances)
                else None,
            })

        # ========================================================
        # DEBUG: SHOW RETRIEVED CHUNKS
        # ========================================================

        print()
        print("=" * 80)
        print("RAG RETRIEVAL")
        print("=" * 80)

        print(f"QUERY:")
        print(query)

        print("-" * 80)

        for i, result in enumerate(output, 1):

            print(f"\nCHUNK #{i}")

            print(
                f"Company : {result['company']}"
            )

            print(
                f"Source  : {result['source']}"
            )

            print(
                f"Distance: {result['distance']}"
            )

            print("-" * 80)

            print(
                result["text"]
            )

            print("-" * 80)

        print("=" * 80)
        print()

        return output