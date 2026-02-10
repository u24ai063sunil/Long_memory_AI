import uuid
from backend.memory.chroma_store import memory_collection


def build_memory_sentence(memory):
    """
    Convert structured memory into a natural language statement.
    This greatly improves embedding similarity search.
    """

    if memory.type == "preference":
        return f"The user prefers {memory.value}."

    if memory.type == "fact":
        return f"A fact about the user: {memory.value}."

    if memory.type == "constraint":
        return f"A constraint to respect: {memory.value}."

    if memory.type == "commitment":
        return f"The user has committed to: {memory.value}."

    if memory.type == "instruction":
        return f"Instruction from user: {memory.value}."

    # fallback
    return memory.value


def store_memory(memory):

    # Create semantic sentence
    memory_text = build_memory_sentence(memory)

    memory_id = str(uuid.uuid4())

    memory_collection.add(
        documents=[memory_text],   # <-- IMPORTANT CHANGE
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
