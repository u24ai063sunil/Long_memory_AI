import uuid
from backend.memory.chroma_store import memory_collection

def store_memory(memory):

    memory_id = str(uuid.uuid4())

    memory_collection.add(
        documents=[memory.value],
        metadatas=[{
            "session_id": memory.session_id,
            "type": memory.type,
            "key": memory.key,
            "confidence": memory.confidence,
            "source_turn": memory.source_turn,
            "last_used_turn": memory.last_used_turn
        }],
        ids=[memory_id]
    )

    return memory_id
