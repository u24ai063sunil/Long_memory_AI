import uuid
from datetime import datetime

from sentence_transformers import SentenceTransformer, util
import numpy as np

from memory.chroma_store import memory_collection
from memory.retrieve import retrieve_by_key


# ---------------------------------------------------------
# EMBEDDING MODEL (for duplicate detection)
# Lazy-load the model to avoid heavy imports at module import time
# ---------------------------------------------------------
_model = None

SIM_THRESHOLD = 0.90   # cosine similarity threshold


def _get_model():
    global _model
    if _model is None:
        # _model = SentenceTransformer("all-MiniLM-L6-v2")
        _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
    return _model


def get_embedding(text, convert_to_tensor=True):
    """Return embedding for `text`. `text` may be a string or list of strings."""
    return _get_model().encode(text, convert_to_tensor=convert_to_tensor)


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
    # compute embedding as a plain list (Chroma expects python lists)
    new_emb = get_embedding(memory_text, convert_to_tensor=False)
    if hasattr(new_emb, "tolist"):
        new_emb = new_emb.tolist()

    # Prefer vector query for efficient duplicate detection
    try:
        # chroma's query API may accept `query_embeddings` (newer) or `embedding`
        try:
            results = memory_collection.query(
                query_embeddings=[new_emb],
                n_results=3,
                where={"session_id": session_id, "is_active": True},
                include=["embeddings"]
            )
        except TypeError:
            results = memory_collection.query(
                embedding=[new_emb],
                n_results=3,
                where={"session_id": session_id, "is_active": True},
                include=["embeddings"]
            )

        emb_lists = results.get("embeddings") or []
        if emb_lists and len(emb_lists) > 0:
            returned = emb_lists[0]
            if returned:
                # compute cosine similarities
                sims = []
                new_arr = np.array(new_emb, dtype=float)
                new_norm = np.linalg.norm(new_arr)
                for e in returned:
                    e_arr = np.array(e, dtype=float)
                    denom = (new_norm * np.linalg.norm(e_arr))
                    if denom == 0:
                        sims.append(0.0)
                    else:
                        sims.append(float(np.dot(new_arr, e_arr) / denom))

                max_score = max(sims) if sims else 0.0
                if max_score > SIM_THRESHOLD:
                    print(f"⚠️ Duplicate skipped (similarity={max_score:.2f})")
                    return True

    except Exception:
        # fallback to previous approach: fetch documents and compare embeddings
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

        # use model tensors for cosine similarity when comparing against raw docs
        new_emb_t = get_embedding(memory_text, convert_to_tensor=True)
        old_emb_t = get_embedding(existing_docs, convert_to_tensor=True)

        scores = util.cos_sim(new_emb_t, old_emb_t)[0]
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

    # compute and store embedding alongside the memory for fast future queries
    emb_to_store = get_embedding(memory_text, convert_to_tensor=False)
    if hasattr(emb_to_store, "tolist"):
        emb_to_store = emb_to_store.tolist()

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
        ids=[memory_id],
        embeddings=[emb_to_store]
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