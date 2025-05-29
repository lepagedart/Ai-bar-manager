from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  # ✅ Fixed line break
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ✅ Updated file path to point to static folder
PDF_PATH = "static/Cocktail Codex PDF.pdf"

# Step 1: Load the PDF
print("📚 Loading PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

# Step 2: Split into manageable chunks
print("✂️ Splitting document into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)

# Step 3: Create OpenAI embeddings
print("🧠 Creating embeddings...")
embeddings = OpenAIEmbeddings()

# Step 4: Save as FAISS vector index
print("📦 Saving FAISS index...")
db = FAISS.from_documents(chunks, embeddings)
db.save_local("codex_faiss_index")

print("✅ Cocktail Codex has been embedded and stored for RAG use.")