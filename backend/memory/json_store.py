"""
Simple JSON-based memory storage with embedding support
Uses TinyDB for storage and HuggingFace API for embeddings
"""
from tinydb import TinyDB, Query
import os
from memory.hf_embeddings import get_embedding, batch_cosine_similarity
import numpy as np

# Initialize database
DB_PATH = os.getenv("MEMORY_DB_PATH", "./memory_store.json")
db = TinyDB(DB_PATH)
memory_table = db.table('memories')

Memory = Query()


def add_memory(memory_data):
    """
    Add a memory to the database
    
    Args:
        memory_data (dict): Memory object with keys:
            - id: str
            - session_id: str
            - type: str
            - key: str
            - value: str
            - text: str (the full memory sentence)
            - embedding: list (384-dim vector from HF API)
            - confidence: float
            - source_turn: int
            - last_used_turn: int
            - is_active: bool
            - updated_at: str
    """
    memory_table.insert(memory_data)


def get_memories(session_id, is_active=True):
    """Get all memories for a session"""
    query = (Memory.session_id == session_id)
    if is_active:
        query &= (Memory.is_active == True)
    
    return memory_table.search(query)


def get_memory_by_key(session_id, key, is_active=True):
    """Get specific memory by key"""
    query = (
        (Memory.session_id == session_id) &
        (Memory.key == key)
    )
    if is_active:
        query &= (Memory.is_active == True)
    
    return memory_table.search(query)


def update_memory(memory_id, updates):
    """Update a memory by ID"""
    memory_table.update(updates, Memory.id == memory_id)


def search_memories_semantic(session_id, query_text, is_active=True, limit=5):
    """
    Search memories using semantic similarity (via HuggingFace API)
    
    Args:
        session_id: Session ID
        query_text: Search query string
        is_active: Only active memories
        limit: Max results
    """
    # Get all memories for this session
    all_memories = get_memories(session_id, is_active)
    
    if not all_memories:
        return []
    
    if not query_text:
        # No query - return most recent
        return sorted(all_memories, 
                     key=lambda x: x.get('source_turn', 0), 
                     reverse=True)[:limit]
    
    # Get query embedding from HuggingFace API
    try:
        query_embedding = get_embedding(query_text)
    except Exception as e:
        print(f"Error getting query embedding: {e}")
        # Fallback to keyword search
        return search_memories_keyword(session_id, query_text, is_active, limit)
    
    # Calculate similarities
    scored_memories = []
    
    for mem in all_memories:
        if 'embedding' not in mem or not mem['embedding']:
            continue
        
        try:
            similarity = batch_cosine_similarity(
                query_embedding,
                [mem['embedding']]
            )[0]
            
            scored_memories.append((similarity, mem))
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            continue
    
    # Sort by similarity and recency
    scored_memories.sort(
        key=lambda x: (x[0], x[1].get('source_turn', 0)), 
        reverse=True
    )
    
    return [mem for score, mem in scored_memories[:limit]]


def search_memories_keyword(session_id, keywords, is_active=True, limit=5):
    """
    Search memories by keywords (simple text matching)
    Fallback when semantic search fails
    """
    all_memories = get_memories(session_id, is_active)
    
    if not keywords:
        return sorted(all_memories, 
                     key=lambda x: x.get('source_turn', 0), 
                     reverse=True)[:limit]
    
    keywords_lower = keywords.lower()
    scored_memories = []
    
    for mem in all_memories:
        text = mem.get('text', '').lower()
        value = mem.get('value', '').lower()
        
        score = 0
        for word in keywords_lower.split():
            if word in text:
                score += 2
            if word in value:
                score += 1
        
        if score > 0:
            scored_memories.append((score, mem))
    
    scored_memories.sort(
        key=lambda x: (x[0], x[1].get('source_turn', 0)), 
        reverse=True
    )
    
    return [mem for score, mem in scored_memories[:limit]]


def delete_database():
    """Delete the entire database (for testing)"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)