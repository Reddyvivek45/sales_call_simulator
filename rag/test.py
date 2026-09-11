from rag.retriever import Retriever


def main():

    retriever = Retriever()

    queries = [
        "How much will FIREAI cost KLM?",
        "Can FIREAI work with our existing CCTV?",
        "What are KLM's fire safety concerns?",
        "How does KLM evaluate a FIREAI purchase?",
        "What would KLM want to evaluate in a pilot?",
        "What are the technical details of KLM's CCTV system?",
        "What are the risks of false alarms for KLM?",
        "What does KLM consider when evaluating ROI?",
        "FIREAI can help improve fire monitoring in your mall.",
    ]

    for query in queries:

        print("\n\n")
        print("#" * 100)
        print("TEST QUERY")
        print("#" * 100)
        print(query)

        results = retriever.search(query)

        print("\nRetrieved sources:")

        for i, result in enumerate(results, 1):

            print(
                f"{i}. "
                f"{result['source']} "
                f"(distance={result['distance']:.4f})"
            )


if __name__ == "__main__":
    main()