from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# Load FAISS index (must exist already)
db = FAISS.load_local("codex_faiss_index", OpenAIEmbeddings())

# Function to retrieve relevant context
def retrieve_codex_context(query):
    docs = db.similarity_search(query, k=3)  # Top 3 relevant chunks
    return "\n\n".join(doc.page_content for doc in docs)