import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client(
    chromadb.Settings(persist_directory="./chroma_memory")
)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    # model_name="all-MiniLM-L6-v2"
    model_name="paraphrase-MiniLM-L3-v2"
)

memory_collection = client.get_or_create_collection(
    name="long_term_memory",
    embedding_function=embedding_function
)
