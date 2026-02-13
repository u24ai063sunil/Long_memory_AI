"""
Memory storage with HuggingFace API embeddings
Uses semantic similarity for duplicate detection
"""
import uuid
from datetime import datetime

from memory.json_store import (
    add_memory, 
    get_memory_by_key, 
    update_memory,
    search_memories_semantic
)
from memory.hf_embeddings import get_embedding, batch_cosine_similarity


SIM_THRESHOLD = 0.90  # Cosine similarity threshold for duplicates


# ---------------------------------------------------------
# MEMORY SENTENCE BUILDER
# ---------------------------------------------------------
def build_memory_sentence(memory):
    """Convert memory object to readable sentence"""
    
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
# SEMANTIC DUPLICATE CHECK (using HF API)
# ---------------------------------------------------------
def is_duplicate(memory_text, session_id):
    """
    Check if similar memory exists using semantic similarity via HuggingFace API
    """
    try:
        # Get embedding for new memory
        new_embedding = get_embedding(memory_text)
        
        # Search for similar memories
        similar = search_memories_semantic(session_id, memory_text, limit=3)
        
        if not similar:
            return False
        
        # Check similarities
        for mem in similar:
            if 'embedding' not in mem or not mem['embedding']:
                continue
            
            similarity = batch_cosine_similarity(
                new_embedding,
                [mem['embedding']]
            )[0]
            
            if similarity > SIM_THRESHOLD:
                print(f"⚠️ Duplicate found (similarity={similarity:.2f}), skipping")
                return True
        
    except Exception as e:
        print(f"Duplicate check error: {e}")
        # If API fails, do basic text matching fallback
        similar = search_memories_semantic(session_id, memory_text, limit=3)
        memory_lower = memory_text.lower()
        
        for mem in similar:
            existing_text = mem.get('text', '').lower()
            if memory_lower == existing_text:
                print(f"⚠️ Exact text match found, skipping")
                return True
    
    return False


# ---------------------------------------------------------
# DEACTIVATE OLD MEMORY (UPDATE LOGIC)
# ---------------------------------------------------------
def deactivate_old_memory(session_id, key):
    """Mark old memories with the same key as inactive"""
    
    existing = get_memory_by_key(session_id, key, is_active=True)
    
    if not existing:
        return
    
    for mem in existing:
        update_memory(
            mem['id'],
            {
                'is_active': False,
                'updated_at': datetime.utcnow().isoformat()
            }
        )
        print(f"♻️ Memory updated → old deactivated: {mem['key']}")


# ---------------------------------------------------------
# CORE STORAGE LOGIC
# ---------------------------------------------------------
def store_memory(memory):
    """Store a memory in the database with HuggingFace embedding"""
    
    memory_text = build_memory_sentence(memory)
    
    # -------- DUPLICATE CHECK --------
    if is_duplicate(memory_text, memory.session_id):
        return None
    
    # -------- UPDATE OLD MEMORY --------
    existing = get_memory_by_key(memory.session_id, memory.key)
    
    if existing:
        deactivate_old_memory(memory.session_id, memory.key)
    
    # -------- GENERATE EMBEDDING VIA HF API --------
    try:
        embedding = get_embedding(memory_text)
        embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    except Exception as e:
        print(f"Warning: Could not generate embedding: {e}")
        embedding_list = None
    
    # -------- STORE NEW MEMORY --------
    memory_id = str(uuid.uuid4())
    
    memory_data = {
        "id": memory_id,
        "session_id": memory.session_id,
        "type": memory.type,
        "key": memory.key,
        "value": memory.value,
        "text": memory_text,
        "embedding": embedding_list,  # Store embedding for future searches
        "confidence": float(memory.confidence),
        "source_turn": int(memory.source_turn),
        "last_used_turn": int(memory.last_used_turn),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": ""
    }
    
    add_memory(memory_data)
    
    print(f"✅ Memory stored: {memory_text}")
    
    return memory_id


# ---------------------------------------------------------
# ASYNC WRAPPER (used by BackgroundTasks)
# ---------------------------------------------------------
def store_memory_async(memory):
    """Async wrapper for background tasks"""
    try:
        store_memory(memory)
    except Exception as e:
        print(f"Memory async storage error: {e}")