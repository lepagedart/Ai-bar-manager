import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Configuration
SOURCE_DIR = "knowledge_base"
VECTOR_INDEX_DIR = "vector_index"

# Embedding model (local, no OpenAI)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Text splitter config
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# Collect and split all documents
all_chunks = []

print("📁 Scanning knowledge_base/ recursively...")

for root, _, files in os.walk(SOURCE_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        ext = Path(file).suffix.lower()

        if ext == ".pdf":
            print(f"📄 Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
        elif ext == ".txt":
            print(f"📄 Loading TXT: {file_path}")
            loader = TextLoader(file_path)
        else:
            print(f"⏭️ Skipping unsupported file: {file_path}")
            continue

        docs = loader.load()
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

# Build vector index
print("🧠 Embedding and saving vector index...")
db = FAISS.from_documents(all_chunks, embedding_model)
db.save_local(VECTOR_INDEX_DIR)

print("✅ All documents embedded and saved to /vector_index/")