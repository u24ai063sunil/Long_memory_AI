import uuid
from datetime import datetime

from sentence_transformers import SentenceTransformer, util

from backend.memory.chroma_store import memory_collection
from backend.memory.retrieve import retrieve_by_key


# ---------------------------------------------------------
# EMBEDDING MODEL (for duplicate detection)
# ---------------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

SIM_THRESHOLD = 0.90   # cosine similarity threshold


# ---------------------------------------------------------
# MEMORY SENTENCE BUILDER
# ---------------------------------------------------------
def build_memory_sentence(memory):

    if memory.type == "preference":
        return f"The user prefers {memory.value}."

    if memory.type == "fact":
        return f"The user is {memory.value}."

    if memory.type == "constraint":
        return f"A constraint to respect: {memory.value}."

    if memory.type == "goal":
        return f"The user wants to {memory.value}."

    if memory.type == "episodic_summary":
        return f"Conversation summary: {memory.value}"

    return memory.value


# ---------------------------------------------------------
# SEMANTIC DUPLICATE CHECK
# ---------------------------------------------------------
def is_duplicate(memory_text, session_id):

    results = memory_collection.get(
        where={
            "$and": [
                {"session_id": session_id},
                {"is_active": True}
            ]
        }
    )

    if not results or not results.get("documents"):
        return False

    existing_docs = results["documents"]

    if len(existing_docs) == 0:
        return False

    new_emb = model.encode(memory_text, convert_to_tensor=True)
    old_emb = model.encode(existing_docs, convert_to_tensor=True)

    scores = util.cos_sim(new_emb, old_emb)[0]

    max_score = float(scores.max())

    if max_score > SIM_THRESHOLD:
        print(f"⚠️ Duplicate skipped (similarity={max_score:.2f})")
        return True

    return False


# ---------------------------------------------------------
# DEACTIVATE OLD MEMORY (UPDATE LOGIC)
# ---------------------------------------------------------
def deactivate_old_memory(session_id, key):

    results = retrieve_by_key(session_id, key)

    if not results or not results["ids"]:
        return

    for id_, meta in zip(results["ids"], results["metadatas"]):

        meta["is_active"] = False
        meta["updated_at"] = datetime.utcnow().isoformat()

        memory_collection.update(
            ids=[id_],
            metadatas=[meta]
        )

        print(f"♻️ Memory updated → old deactivated: {meta['key']}")


# ---------------------------------------------------------
# CORE STORAGE LOGIC
# ---------------------------------------------------------
def store_memory(memory):

    memory_text = build_memory_sentence(memory)

    # -------- DUPLICATE CHECK --------
    if is_duplicate(memory_text, memory.session_id):
        return None

    # -------- UPDATE OLD MEMORY --------
    existing = retrieve_by_key(memory.session_id, memory.key)

    if existing and existing["ids"]:
        deactivate_old_memory(memory.session_id, memory.key)

    # -------- STORE NEW MEMORY --------
    memory_id = str(uuid.uuid4())

    memory_collection.add(
        documents=[memory_text],
        metadatas=[{
            "session_id": memory.session_id,
            "type": memory.type,
            "key": memory.key,
            "confidence": float(memory.confidence),
            "source_turn": int(memory.source_turn),
            "last_used_turn": int(memory.last_used_turn),
            "is_active": True,
            "updated_at": ""   # never None (Chroma safe)
        }],
        ids=[memory_id]
    )

    print(f"✅ Memory stored (active): {memory_text}")

    return memory_id


# ---------------------------------------------------------
# ASYNC WRAPPER (used by BackgroundTasks)
# ---------------------------------------------------------
def store_memory_async(memory):

    try:
        store_memory(memory)
    except Exception as e:
        print("Memory async storage error:", e)
