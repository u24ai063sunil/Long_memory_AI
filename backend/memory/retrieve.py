# from memory.chroma_store import memory_collection


# def retrieve_memories(session_id, query, k=5):

#     results = memory_collection.query(
#         query_texts=[query],
#         n_results=k,
#         where={
#             "$and": [
#                 {"session_id": session_id},
#                 {"is_active": True}
#             ]
#         }
#     )

#     memories = []

#     for doc, meta, id_ in zip(
#         results["documents"][0],
#         results["metadatas"][0],
#         results["ids"][0]
#     ):
#         memories.append({
#             "id": id_,
#             "text": doc,
#             "meta": meta
#         })

#     return memories


# # -------- KEY LOOKUP FOR UPDATE --------
# def retrieve_by_key(session_id, key):

#     results = memory_collection.get(
#         where={
#             "$and": [
#                 {"session_id": session_id},
#                 {"key": key},
#                 {"is_active": True}
#             ]
#         }
#     )

#     return results
"""
Memory retrieval with semantic search via HuggingFace API
"""
from memory.json_store import search_memories_semantic, get_memory_by_key


def retrieve_memories(session_id, query, k=5):
    """
    Retrieve relevant memories for a query using semantic search
    
    Args:
        session_id: User session ID
        query: Search query string
        k: Number of memories to return
    
    Returns:
        List of memory dictionaries
    """
    
    # Use semantic search via HuggingFace API
    memories = search_memories_semantic(session_id, query, limit=k)
    
    # Format to match expected structure
    formatted_memories = []
    
    for mem in memories:
        formatted_memories.append({
            "id": mem.get("id"),
            "text": mem.get("text"),
            "meta": {
                "session_id": mem.get("session_id"),
                "type": mem.get("type"),
                "key": mem.get("key"),
                "confidence": mem.get("confidence"),
                "source_turn": mem.get("source_turn"),
                "last_used_turn": mem.get("last_used_turn"),
                "is_active": mem.get("is_active")
            }
        })
    
    return formatted_memories


def retrieve_by_key(session_id, key):
    """
    Retrieve memory by specific key
    
    Args:
        session_id: User session ID
        key: Memory key
    
    Returns:
        Dictionary with 'ids' and 'metadatas' keys (for compatibility)
    """
    
    memories = get_memory_by_key(session_id, key, is_active=True)
    
    if not memories:
        return {"ids": [], "metadatas": []}
    
    ids = [m.get("id") for m in memories]
    metadatas = [
        {
            "session_id": m.get("session_id"),
            "type": m.get("type"),
            "key": m.get("key"),
            "confidence": m.get("confidence"),
            "source_turn": m.get("source_turn"),
            "last_used_turn": m.get("last_used_turn"),
            "is_active": m.get("is_active"),
            "updated_at": m.get("updated_at", "")
        }
        for m in memories
    ]
    
    return {
        "ids": ids,
        "metadatas": metadatas
    }