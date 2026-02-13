import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.Client(
    chromadb.Settings(persist_directory="./chroma_memory")
)

# Use OpenAI embeddings via API instead of local model
embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("HF_API_KEY"),
    model_name="all-MiniLM-L6-v2"  # Cheap and fast: $0.02 per 1M tokens
)

memory_collection = client.get_or_create_collection(
    name="long_term_memory",
    embedding_function=embedding_function
)