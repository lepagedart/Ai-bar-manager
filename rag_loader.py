from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# ✅ PDF location (must match where you stored it)
PDF_PATH = "static/Cocktail Codex PDF.pdf"

# ✅ Step 1: Load the PDF
print("📚 Loading PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

# ✅ Step 2: Split into manageable chunks
print("✂️ Splitting document into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)

# ✅ Step 3: Use local HuggingFace embeddings
print("🧠 Creating local embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ✅ Step 4: Save the FAISS vector index
print("📦 Saving FAISS index locally...")
db = FAISS.from_documents(chunks, embeddings)
db.save_local("codex_faiss_index")

print("✅ RAG embedding with HuggingFace complete.")