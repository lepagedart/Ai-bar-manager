from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

# Load .env variables
load_dotenv()

# Path to FAISS index folder
VECTOR_INDEX_PATH = "codex_faiss_index"

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

loader = DirectoryLoader(
    "./knowledge_base",
    glob="**/*.pdf",
    show_progress=True,
    loader_cls=PyPDFLoader
)
docs = loader.load()
print(f"[DEBUG] Number of documents loaded: {len(docs)}")
for i, doc in enumerate(docs[:5]):  # Limit output to 5 docs for brevity
    print(f"[DEBUG] Document {i+1}: {doc.metadata.get('source')}")
    
from langchain_community.document_loaders import TextLoader

txt_loader = DirectoryLoader(
    "./knowledge_base",
    glob="**/*.txt",
    show_progress=True,
    loader_cls=TextLoader
)

txt_docs = txt_loader.load()
print(f"[DEBUG] Number of text documents loaded: {len(txt_docs)}")
for i, doc in enumerate(txt_docs[:5]):
    print(f"[DEBUG] Text Document {i+1}: {doc.metadata.get('source')}")

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