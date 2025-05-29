from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Load FAISS index from local directory
db = FAISS.load_local(
    "codex_faiss_index",
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
)

# ✅ Function to retrieve relevant context for a query
def retrieve_codex_context(query):
    docs = db.similarity_search(query, k=3)  # top 3 chunks
    return "\n\n".join(doc.page_content for doc in docs)