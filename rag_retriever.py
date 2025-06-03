from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Path to FAISS index folder
VECTOR_INDEX_PATH = "codex_faiss_index"

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the FAISS vector store from disk
db = FAISS.load_local(
    VECTOR_INDEX_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# Function to retrieve relevant context based on a query
def retrieve_codex_context(query: str) -> str:
    vectorstore = FAISS.load_local(
        VECTOR_INDEX_PATH,
        embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
        allow_dangerous_deserialization=True
    )
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])