from rag_retriever import retrieve_codex_context

context = retrieve_codex_context("What is the difference between a sour and a fizz?")
print("\n=== Retrieved Context ===")
print(context)