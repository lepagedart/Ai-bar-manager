from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

# Load FAISS index from the new vector_index directory
VECTOR_INDEX_PATH = "vector_index"
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = FAISS.load_local(VECTOR_INDEX_PATH, embeddings=embedding_model, allow_dangerous_deserialization=True)

# Function to retrieve relevant context from the vector DB
def retrieve_codex_context(query):
    docs = db.similarity_search(query, k=3)
    return "\n\n".join(doc.page_content for doc in docs)