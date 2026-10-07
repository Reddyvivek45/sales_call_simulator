from pathlib import Path
import pickle
import re

import chromadb

from sentence_transformers import SentenceTransformer

from rank_bm25 import BM25Okapi

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)


# ============================================================
# BM25 STORAGE
# ============================================================

BM25_DIR = Path(CHROMA_DIR) / "bm25"

BM25_INDEX_FILE = (
    BM25_DIR / "bm25_index.pkl"
)

BM25_DOCUMENTS_FILE = (
    BM25_DIR / "bm25_documents.pkl"
)


# ============================================================
# RETRIEVER
# ============================================================

class Retriever:


    def __init__(self):

        print(
            "[RETRIEVER] Loading embedding model..."
        )


        # ====================================================
        # SENTENCE TRANSFORMER
        # ====================================================

        self.embedding_model = (
            SentenceTransformer(
                EMBEDDING_MODEL
            )
        )


        # ====================================================
        # CHROMADB
        # ====================================================

        print(
            "[RETRIEVER] Connecting to ChromaDB..."
        )


        self.client = (
            chromadb.PersistentClient(
                path=str(CHROMA_DIR)
            )
        )


        self.collection = (
            self.client.get_collection(
                COLLECTION_NAME
            )
        )


        # ====================================================
        # LOAD BM25
        # ====================================================

        print(
            "[RETRIEVER] Loading BM25 index..."
        )


        if not BM25_INDEX_FILE.exists():

            raise FileNotFoundError(

                "BM25 index not found. "

                "Run rag/ingest.py first."

            )


        if not BM25_DOCUMENTS_FILE.exists():

            raise FileNotFoundError(

                "BM25 document store not found. "

                "Run rag/ingest.py first."

            )


        with open(
            BM25_INDEX_FILE,
            "rb",
        ) as file:

            self.bm25 = pickle.load(
                file
            )


        with open(
            BM25_DOCUMENTS_FILE,
            "rb",
        ) as file:

            self.bm25_documents = (
                pickle.load(file)
            )


        self.bm25_ids = (
            self.bm25_documents["ids"]
        )


        self.bm25_texts = (
            self.bm25_documents["texts"]
        )


        self.bm25_metadatas = (
            self.bm25_documents["metadatas"]
        )


        print(
            "[RETRIEVER] Ready."
        )


    # ========================================================
    # TOKENIZER
    # ========================================================

    @staticmethod
    def tokenize(text):

        return text.lower().split()


    # ========================================================
    # SEMANTIC SEARCH
    # ========================================================

    def semantic_search(
        self,
        query,
        top_k=8,
    ):

        query_embedding = (
            self.embedding_model.encode(

                query,

                normalize_embeddings=True,

            ).tolist()
        )


        results = self.collection.query(

            query_embeddings=[
                query_embedding
            ],

            n_results=top_k,

        )


        documents = results.get(
            "documents",
            [[]],
        )[0]


        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]


        distances = results.get(
            "distances",
            [[]],
        )[0]


        ids = results.get(
            "ids",
            [[]],
        )[0]


        output = []


        for i, document in enumerate(
            documents
        ):

            metadata = (
                metadatas[i]
                if i < len(metadatas)
                else {}
            )


            output.append({

                "id":
                    ids[i]
                    if i < len(ids)
                    else None,

                "text":
                    document,

                "company":
                    metadata.get(
                        "company",
                        "unknown",
                    ),

                "source":
                    metadata.get(
                        "source",
                        "unknown",
                    ),
                "topic": metadata.get("topic", "unknown"),

                "distance":
                    distances[i]
                    if i < len(distances)
                    else None,

            })


        return output


    # ========================================================
    # BM25 SEARCH
    # ========================================================

    def bm25_search(
        self,
        query,
        top_k=8,
    ):

        tokenized_query = (
            self.tokenize(query)
        )


        scores = self.bm25.get_scores(
            tokenized_query
        )


        ranked_indices = sorted(

            range(len(scores)),

            key=lambda index:
                scores[index],

            reverse=True,

        )


        output = []


        for index in ranked_indices[:top_k]:

            output.append({

                "id":
                    self.bm25_ids[index],

                "text":
                    self.bm25_texts[index],

                "company":
                    self.bm25_metadatas[index].get(
                        "company",
                        "unknown",
                    ),

                "source":
                    self.bm25_metadatas[index].get(
                        "source",
                        "unknown",
                    ),
                "topic": self.bm25_metadatas[index].get("topic", "unknown"),

                "bm25_score":
                    float(scores[index]),

            })


        return output


    # ========================================================
    # RECIPROCAL RANK FUSION
    # ========================================================

    def reciprocal_rank_fusion(
        self,
        semantic_results,
        bm25_results,
        k=60,
    ):

        fused = {}


        # ====================================================
        # SEMANTIC RANKING
        # ====================================================

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):

            document_id = result["id"]


            if document_id not in fused:

                fused[document_id] = {

                    "id":
                        document_id,

                    "text":
                        result["text"],

                    "company":
                        result["company"],

                    "source":
                        result["source"],

                    "semantic_rank":
                        rank,

                    "bm25_rank":
                        None,

                    "semantic_distance":
                        result.get(
                            "distance"
                        ),

                    "bm25_score":
                        None,

                    "rrf_score":
                        0.0,

                }


            fused[
                document_id
            ]["rrf_score"] += (
                1.0 /
                (k + rank)
            )


        # ====================================================
        # BM25 RANKING
        # ====================================================

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):

            document_id = result["id"]


            if document_id not in fused:

                fused[document_id] = {

                    "id":
                        document_id,

                    "text":
                        result["text"],

                    "company":
                        result["company"],

                    "source":
                        result["source"],

                    "semantic_rank":
                        None,

                    "bm25_rank":
                        rank,

                    "semantic_distance":
                        None,

                    "bm25_score":
                        result.get(
                            "bm25_score"
                        ),

                    "rrf_score":
                        0.0,

                }


            else:

                fused[
                    document_id
                ]["bm25_rank"] = rank

                fused[
                    document_id
                ]["bm25_score"] = (
                    result.get(
                        "bm25_score"
                    )
                )


            fused[
                document_id
            ]["rrf_score"] += (
                1.0 /
                (k + rank)
            )


        # ====================================================
        # SORT BY RRF SCORE
        # ====================================================

        results = sorted(

            fused.values(),

            key=lambda item:
                item["rrf_score"],

            reverse=True,

        )


        return results


    # ========================================================
    # MAIN SEARCH
    # ========================================================

    def search(
        self,
        query,
        top_k=TOP_K,
    ):

        # ====================================================
        # RETRIEVE MORE CANDIDATES
        # ====================================================

        candidate_k = max(
            top_k * 2,
            8,
        )


        # ====================================================
        # SEMANTIC RETRIEVAL
        # ====================================================

        semantic_results = (
            self.semantic_search(
                query,
                top_k=candidate_k,
            )
        )


        # ====================================================
        # BM25 RETRIEVAL
        # ====================================================

        bm25_results = (
            self.bm25_search(
                query,
                top_k=candidate_k,
            )
        )


        # ====================================================
        # RRF
        # ====================================================

        fused_results = (
            self.reciprocal_rank_fusion(
                semantic_results,
                bm25_results,
            )
        )


        # ====================================================
        # FINAL TOP K
        # ====================================================

        output = fused_results[
            :top_k
        ]


        # ====================================================
        # DEBUG
        # ====================================================

        print()
        print("=" * 80)
        print("HYBRID RAG RETRIEVAL")
        print("=" * 80)

        print()
        print("QUERY:")
        print(query)

        print()
        print("-" * 80)
        print("SEMANTIC RESULTS")
        print("-" * 80)


        for i, result in enumerate(
            semantic_results,
            start=1,
        ):

            print()
            print(
                f"#{i} "
                f"{result['id']}"
            )

            print(
                f"Company : "
                f"{result['company']}"
            )

            print(
                f"Source  : "
                f"{result['source']}"
            )

            print(
                f"Distance: "
                f"{result['distance']}"
            )


        print()
        print("-" * 80)
        print("BM25 RESULTS")
        print("-" * 80)


        for i, result in enumerate(
            bm25_results,
            start=1,
        ):

            print()
            print(
                f"#{i} "
                f"{result['id']}"
            )

            print(
                f"Company : "
                f"{result['company']}"
            )

            print(
                f"Source  : "
                f"{result['source']}"
            )

            print(
                f"BM25    : "
                f"{result['bm25_score']:.4f}"
            )


        print()
        print("-" * 80)
        print("RRF FINAL RESULTS")
        print("-" * 80)


        for i, result in enumerate(
            output,
            start=1,
        ):

            print()
            print(
                f"#{i} "
                f"{result['id']}"
            )

            print(
                f"Company : "
                f"{result['company']}"
            )

            print(
                f"Source  : "
                f"{result['source']}"
            )

            print(
                f"Semantic Rank : "
                f"{result['semantic_rank']}"
            )

            print(
                f"BM25 Rank : "
                f"{result['bm25_rank']}"
            )

            print(
                f"RRF Score : "
                f"{result['rrf_score']:.6f}"
            )

            print("-" * 80)

            print(
                result["text"]
            )

            print("-" * 80)


        print("=" * 80)
        print()


        return output