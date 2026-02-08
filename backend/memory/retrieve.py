from backend.memory.chroma_store import memory_collection

def retrieve_memories(session_id, query, k=5):

    results = memory_collection.query(
        query_texts=[query],
        n_results=k,
        where={"session_id": session_id}
    )

    memories = []

    for doc, meta, id_ in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0]
    ):
        memories.append({
            "id": id_,
            "text": doc,
            "meta": meta
        })

    return memories
