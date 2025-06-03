from rag_retriever import retrieve_codex_context

if __name__ == "__main__":
    query = "What is the proper ratio for a sour cocktail?"
    context = retrieve_codex_context(query)
    print("\n--- Retrieved Context ---\n")
    print(context)