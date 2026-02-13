# """
# Memory retrieval with semantic search via HuggingFace API
# """
# from memory.json_store import search_memories_semantic, get_memory_by_key


# def retrieve_memories(session_id, query, k=5):
#     """
#     Retrieve relevant memories for a query using semantic search
    
#     Args:
#         session_id: User session ID
#         query: Search query string
#         k: Number of memories to return
    
#     Returns:
#         List of memory dictionaries
#     """
    
#     # Use semantic search via HuggingFace API
#     memories = search_memories_semantic(session_id, query, limit=k)
    
#     # Format to match expected structure
#     formatted_memories = []
    
#     for mem in memories:
#         formatted_memories.append({
#             "id": mem.get("id"),
#             "text": mem.get("text"),
#             "meta": {
#                 "session_id": mem.get("session_id"),
#                 "type": mem.get("type"),
#                 "key": mem.get("key"),
#                 "confidence": mem.get("confidence"),
#                 "source_turn": mem.get("source_turn"),
#                 "last_used_turn": mem.get("last_used_turn"),
#                 "is_active": mem.get("is_active")
#             }
#         })
    
#     return formatted_memories


# def retrieve_by_key(session_id, key):
#     """
#     Retrieve memory by specific key
    
#     Args:
#         session_id: User session ID
#         key: Memory key
    
#     Returns:
#         Dictionary with 'ids' and 'metadatas' keys (for compatibility)
#     """
    
#     memories = get_memory_by_key(session_id, key, is_active=True)
    
#     if not memories:
#         return {"ids": [], "metadatas": []}
    
#     ids = [m.get("id") for m in memories]
#     metadatas = [
#         {
#             "session_id": m.get("session_id"),
#             "type": m.get("type"),
#             "key": m.get("key"),
#             "confidence": m.get("confidence"),
#             "source_turn": m.get("source_turn"),
#             "last_used_turn": m.get("last_used_turn"),
#             "is_active": m.get("is_active"),
#             "updated_at": m.get("updated_at", "")
#         }
#         for m in memories
#     ]
    
#     return {
#         "ids": ids,
#         "metadatas": metadatas
#     }
"""
Enhanced Memory Retrieval with Advanced Ranking
Optimized for accuracy and recall over 1000+ turns

IMPROVEMENTS:
1. Multi-stage retrieval pipeline
2. Context-aware retrieval
3. Dynamic result count based on query complexity
4. Memory clustering for related information
5. Fallback strategies for robustness
"""

from memory.json_store import (
    search_memories_hybrid,
    get_memory_by_key,
    get_memories,
    consolidate_duplicate_memories
)
from typing import List, Dict, Any, Optional
import logging
import re
import os

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.5"))
MAX_MEMORIES_PER_RETRIEVAL = int(os.getenv("MAX_RETRIEVED_MEMORIES", "20"))

# ============================================
# QUERY ANALYSIS
# ============================================

def analyze_query(query: str) -> Dict[str, Any]:
    """
    Analyze query to determine retrieval strategy
    
    IMPROVEMENT: Better query understanding leads to better retrieval
    """
    query_lower = query.lower()
    
    # Detect query intent
    is_question = query.strip().endswith('?')
    is_preference_query = any(word in query_lower for word in ['like', 'prefer', 'favorite', 'love', 'hate'])
    is_fact_query = any(word in query_lower for word in ['what', 'who', 'where', 'when', 'how'])
    is_constraint_query = any(word in query_lower for word in ['can', 'cannot', 'must', 'should', 'allergic', 'restricted'])
    is_temporal = any(word in query_lower for word in ['today', 'tomorrow', 'yesterday', 'schedule', 'time', 'when'])
    
    # Detect mentioned topics
    topics = extract_topics(query)
    
    # Determine complexity
    word_count = len(query.split())
    is_complex = word_count > 10 or is_question
    
    return {
        'is_question': is_question,
        'is_preference_query': is_preference_query,
        'is_fact_query': is_fact_query,
        'is_constraint_query': is_constraint_query,
        'is_temporal': is_temporal,
        'topics': topics,
        'is_complex': is_complex,
        'word_count': word_count
    }


def extract_topics(text: str) -> List[str]:
    """
    Extract potential topics from query
    
    IMPROVEMENT: Topic-based filtering improves precision
    """
    # Common topic keywords
    topic_map = {
        'food': ['food', 'eat', 'restaurant', 'meal', 'diet', 'vegetarian', 'vegan', 'cuisine'],
        'work': ['work', 'job', 'project', 'meeting', 'deadline', 'task', 'office'],
        'health': ['health', 'doctor', 'medicine', 'exercise', 'fitness', 'allergic', 'diet'],
        'schedule': ['time', 'schedule', 'calendar', 'appointment', 'meeting', 'call'],
        'learning': ['learn', 'study', 'course', 'exam', 'homework', 'practice', 'training'],
        'hobby': ['hobby', 'interest', 'passion', 'enjoy', 'fun', 'game', 'music', 'movie'],
    }
    
    text_lower = text.lower()
    detected_topics = []
    
    for topic, keywords in topic_map.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_topics.append(topic)
    
    return detected_topics


# ============================================
# MAIN RETRIEVAL FUNCTION (IMPROVED)
# ============================================

def retrieve_memories(
    session_id: str,
    query: str,
    k: int = 5,
    current_turn: int = None,
    min_confidence: float = MIN_CONFIDENCE
) -> List[Dict[str, Any]]:
    """
    IMPROVED: Multi-stage retrieval with context awareness
    
    Pipeline:
    1. Analyze query
    2. Determine memory types to search
    3. Hybrid search with filters
    4. Post-process and cluster related memories
    5. Format results
    
    Args:
        session_id: User session ID
        query: Search query string
        k: Number of memories to return (dynamic based on query)
        current_turn: Current conversation turn
        min_confidence: Minimum confidence threshold
    
    Returns:
        List of formatted memory dictionaries
    """
    
    try:
        # Stage 1: Query Analysis
        query_analysis = analyze_query(query) if query else {}
        
        # Stage 2: Determine search parameters
        memory_types = _determine_memory_types(query_analysis)
        
        # Adjust k based on query complexity
        if query_analysis.get('is_complex'):
            k = min(k + 3, MAX_MEMORIES_PER_RETRIEVAL)
        
        # Stage 3: Hybrid Search
        memories = search_memories_hybrid(
            session_id=session_id,
            query_text=query,
            current_turn=current_turn,
            is_active=True,
            limit=k * 2,  # Get more, then filter
            min_confidence=min_confidence,
            memory_types=memory_types
        )
        
        if not memories:
            logger.info(f"No memories found for query: {query[:50]}...")
            return []
        
        # Stage 4: Post-process
        memories = _post_process_memories(memories, query_analysis, current_turn)
        
        # Stage 5: Get related memories if available
        memories = _expand_with_related(memories, session_id, current_turn, k)
        
        # Limit to k
        memories = memories[:k]
        
        # Stage 6: Format results
        formatted_memories = _format_memories(memories)
        
        logger.info(f"Retrieved {len(formatted_memories)} memories for query")
        
        # Periodic consolidation (every 100 retrievals, random check)
        import random
        if random.random() < 0.01:  # 1% chance
            consolidate_duplicate_memories(session_id)
        
        return formatted_memories
        
    except Exception as e:
        logger.error(f"Error in retrieve_memories: {e}", exc_info=True)
        return []


def _determine_memory_types(query_analysis: Dict) -> Optional[List[str]]:
    """
    Determine which memory types to prioritize based on query
    
    IMPROVEMENT: Type-based filtering improves precision
    """
    if not query_analysis:
        return None
    
    memory_types = []
    
    if query_analysis.get('is_preference_query'):
        memory_types.extend(['preference', 'fact'])
    
    if query_analysis.get('is_constraint_query'):
        memory_types.extend(['constraint', 'preference'])
    
    if query_analysis.get('is_fact_query'):
        memory_types.extend(['fact', 'goal', 'habit'])
    
    if query_analysis.get('is_temporal'):
        memory_types.extend(['habit', 'constraint'])
    
    # If no specific types detected, return None (search all types)
    return list(set(memory_types)) if memory_types else None


def _post_process_memories(
    memories: List[Dict],
    query_analysis: Dict,
    current_turn: int
) -> List[Dict]:
    """
    Post-process memories to improve relevance
    
    IMPROVEMENT: Additional filtering and boosting based on context
    """
    if not memories:
        return []
    
    processed = []
    
    for mem in memories:
        # Boost score for topic matches
        if query_analysis.get('topics'):
            mem_tags = mem.get('tags', [])
            matching_topics = set(query_analysis['topics']) & set(mem_tags)
            
            if matching_topics:
                # Store original importance for reference
                mem['relevance_boost'] = len(matching_topics) * 0.1
        
        # Boost constraints and preferences for constraint queries
        if query_analysis.get('is_constraint_query'):
            if mem.get('type') in ['constraint', 'preference']:
                mem['relevance_boost'] = mem.get('relevance_boost', 0) + 0.2
        
        processed.append(mem)
    
    # Re-sort by combined score
    if any('relevance_boost' in m for m in processed):
        processed.sort(
            key=lambda x: (
                x.get('importance_score', 0) + x.get('relevance_boost', 0),
                x.get('access_count', 0)
            ),
            reverse=True
        )
    
    return processed


def _expand_with_related(
    memories: List[Dict],
    session_id: str,
    current_turn: int,
    target_count: int
) -> List[Dict]:
    """
    Expand results with related memories if available
    
    IMPROVEMENT: Memory graphs enable better context retrieval
    """
    if len(memories) >= target_count:
        return memories
    
    # Collect related memory IDs
    related_ids = set()
    for mem in memories:
        related_ids.update(mem.get('related_memories', []))
    
    if not related_ids:
        return memories
    
    # Fetch related memories
    existing_ids = {m['id'] for m in memories}
    related_ids -= existing_ids  # Remove already retrieved
    
    if not related_ids:
        return memories
    
    # Get related memories
    from memory.json_store import get_memory_by_id
    
    related_memories = []
    for mem_id in related_ids:
        mem = get_memory_by_id(mem_id)
        if mem and mem.get('is_active'):
            related_memories.append(mem)
    
    # Add to results (with lower priority)
    for mem in related_memories:
        mem['is_related'] = True
    
    # Combine and limit
    all_memories = memories + related_memories[:target_count - len(memories)]
    
    return all_memories


def _format_memories(memories: List[Dict]) -> List[Dict[str, Any]]:
    """
    Format memories to expected structure
    
    IMPROVEMENT: Consistent output format with metadata
    """
    formatted = []
    
    for mem in memories:
        formatted.append({
            "id": mem.get("id"),
            "text": mem.get("text"),
            "meta": {
                "session_id": mem.get("session_id"),
                "type": mem.get("type"),
                "key": mem.get("key"),
                "confidence": mem.get("confidence"),
                "importance_score": mem.get("importance_score", 0.5),
                "source_turn": mem.get("source_turn"),
                "last_used_turn": mem.get("last_used_turn"),
                "access_count": mem.get("access_count", 0),
                "is_active": mem.get("is_active"),
                "tags": mem.get("tags", []),
                "is_related": mem.get("is_related", False)
            }
        })
    
    return formatted


# ============================================
# SPECIALIZED RETRIEVAL FUNCTIONS
# ============================================

def retrieve_by_key(session_id: str, key: str) -> Dict[str, List]:
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
            "importance_score": m.get("importance_score", 0.5),
            "source_turn": m.get("source_turn"),
            "last_used_turn": m.get("last_used_turn"),
            "access_count": m.get("access_count", 0),
            "is_active": m.get("is_active"),
            "updated_at": m.get("updated_at", "")
        }
        for m in memories
    ]
    
    return {
        "ids": ids,
        "metadatas": metadatas
    }


def retrieve_by_type(
    session_id: str,
    memory_type: str,
    limit: int = 10
) -> List[Dict]:
    """
    Retrieve all memories of a specific type
    Useful for specialized queries
    """
    memories = search_memories_hybrid(
        session_id=session_id,
        query_text="",
        is_active=True,
        limit=limit,
        memory_types=[memory_type]
    )
    
    return _format_memories(memories)


def retrieve_recent(
    session_id: str,
    limit: int = 5,
    turns_back: int = 50
) -> List[Dict]:
    """
    Retrieve recent memories within N turns
    Useful for short-term context
    """
    from memory.json_store import get_memories
    
    all_memories = get_memories(session_id, is_active=True)
    
    # Filter by recency
    recent = [
        m for m in all_memories
        if m.get('source_turn', 0) > (max(m.get('source_turn', 0) for m in all_memories) - turns_back)
    ]
    
    # Sort by turn
    recent.sort(key=lambda x: x.get('source_turn', 0), reverse=True)
    
    return _format_memories(recent[:limit])


def get_all_memories(session_id: str, limit: int = 50) -> List[Dict]:
    """
    Get all memories for admin/debugging
    """
    memories = get_memories(session_id, is_active=True, limit=limit)
    return _format_memories(memories)


# MISSING IMPORT FIX
import os


# SUMMARY OF IMPROVEMENTS:
#
# 1. **Query Analysis**
#    - Understands query intent (question, preference, constraint, etc.)
#    - Detects topics for better filtering
#    - Adjusts retrieval strategy based on complexity
#
# 2. **Multi-Stage Retrieval**
#    - Hybrid search (semantic + keyword + metadata)
#    - Post-processing with relevance boosting
#    - Related memory expansion
#    - Smart result limiting
#
# 3. **Type-Based Filtering**
#    - Preference queries prioritize preference/fact memories
#    - Constraint queries prioritize constraint/preference
#    - Better precision through targeted search
#
# 4. **Related Memory Expansion**
#    - Uses related_memories field from schema
#    - Provides better context by including related info
#    - Maintains relevance through smart ordering
#
# 5. **Specialized Retrieval**
#    - retrieve_by_type: Get specific memory categories
#    - retrieve_recent: Short-term context
#    - retrieve_by_key: Direct lookup
#
# 6. **Periodic Consolidation**
#    - Randomly triggers duplicate cleanup
#    - Prevents database bloat over time
#    - Maintains performance at scale