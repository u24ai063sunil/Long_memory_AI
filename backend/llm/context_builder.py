# def build_context(memories):

#     # no memories retrieved
#     if not memories or not isinstance(memories, list):
#         return ""

#     context_lines = []

#     for m in memories:
#         try:
#             # safe extraction
#             meta = m.get("meta", {})
#             value = m.get("text", "")

#             if not value:
#                 continue

#             key = meta.get("key", "")

#             # special handling for call preference
#             if key == "call_time":
#                 context_lines.append(
#                     f"The user prefers to be contacted {value}."
#                 )
#             else:
#                 context_lines.append(value)

#         except Exception as e:
#             print("Context parse error:", e)
#             continue

#     # if nothing usable
#     if not context_lines:
#         return ""

#     context = "IMPORTANT USER FACTS:\n"
#     for line in context_lines:
#         context += f"- {line}\n"

#     context += "\nUse these facts when relevant while answering."

#     return context
"""
Context Builder Module
Builds formatted context from ranked memories for LLM consumption
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
MAX_CONTEXT_MEMORIES = 10  # Maximum memories to include in context
MAX_CONTEXT_LENGTH = 2000  # Maximum character length for context

# ============================================
# CONTEXT FORMATTING
# ============================================
def format_memory_for_context(memory: Dict[str, Any]) -> Optional[str]:
    """
    Format a single memory into a context string
    
    Args:
        memory: Memory dictionary with text and metadata
        
    Returns:
        Formatted string or None if invalid
    """
    try:
        # Extract memory value/text
        value = memory.get("text", "") or memory.get("value", "")
        
        if not value or not value.strip():
            return None
        
        # Get metadata
        meta = memory.get("meta", {})
        memory_type = meta.get("type", "fact")
        key = meta.get("key", "")
        confidence = meta.get("confidence", 0.0)
        
        # Skip low-confidence memories
        if confidence < 0.5:
            logger.debug(f"Skipping low-confidence memory: {key} ({confidence})")
            return None
        
        # Format based on memory type
        if memory_type == "preference":
            return f"User preference: {value}"
        elif memory_type == "constraint":
            return f"Important constraint: {value}"
        elif memory_type == "goal":
            return f"User goal: {value}"
        elif memory_type == "habit":
            return f"User habit: {value}"
        else:
            return value
            
    except Exception as e:
        logger.error(f"Error formatting memory: {e}")
        return None

def deduplicate_memories(formatted_memories: List[str]) -> List[str]:
    """
    Remove duplicate or very similar memories
    
    Args:
        formatted_memories: List of formatted memory strings
        
    Returns:
        Deduplicated list
    """
    seen = set()
    unique = []
    
    for memory in formatted_memories:
        # Create a simple key for deduplication (first 50 chars, lowercased)
        key = memory[:50].lower().strip()
        
        if key not in seen:
            seen.add(key)
            unique.append(memory)
    
    return unique

# ============================================
# MAIN CONTEXT BUILDER
# ============================================
def build_context(memories: List[Dict[str, Any]]) -> str:
    """
    Build formatted context string from memories
    
    Args:
        memories: List of ranked memory dictionaries
        
    Returns:
        Formatted context string for LLM
    """
    try:
        # Validate input
        if not memories or not isinstance(memories, list):
            logger.debug("No memories provided for context")
            return ""
        
        # Format each memory
        formatted_memories = []
        for memory in memories[:MAX_CONTEXT_MEMORIES]:
            formatted = format_memory_for_context(memory)
            if formatted:
                formatted_memories.append(formatted)
        
        # Deduplicate
        formatted_memories = deduplicate_memories(formatted_memories)
        
        # Check if we have any valid memories
        if not formatted_memories:
            logger.debug("No valid memories after formatting")
            return ""
        
        # Build context
        context = "IMPORTANT USER FACTS:\n\n"
        
        for i, memory in enumerate(formatted_memories, 1):
            context += f"{i}. {memory}\n"
        
        context += "\nUse these facts naturally when relevant to the conversation."
        
        # Trim if too long
        if len(context) > MAX_CONTEXT_LENGTH:
            logger.warning(f"Context too long ({len(context)} chars), trimming...")
            # Keep header and trim memories
            header = "IMPORTANT USER FACTS:\n\n"
            footer = "\n\nUse these facts naturally when relevant to the conversation."
            
            available_length = MAX_CONTEXT_LENGTH - len(header) - len(footer)
            trimmed_memories = []
            current_length = 0
            
            for i, memory in enumerate(formatted_memories, 1):
                memory_text = f"{i}. {memory}\n"
                if current_length + len(memory_text) <= available_length:
                    trimmed_memories.append(memory_text)
                    current_length += len(memory_text)
                else:
                    break
            
            context = header + "".join(trimmed_memories) + footer
        
        logger.info(f"Built context with {len(formatted_memories)} memories ({len(context)} chars)")
        return context
        
    except Exception as e:
        logger.error(f"Error building context: {e}", exc_info=True)
        return ""

# ============================================
# ADVANCED CONTEXT BUILDING (OPTIONAL)
# ============================================
def build_structured_context(memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build structured context with categories
    Useful for more sophisticated prompting
    
    Args:
        memories: List of ranked memory dictionaries
        
    Returns:
        Structured context dictionary
    """
    try:
        categories = {
            "preferences": [],
            "facts": [],
            "constraints": [],
            "goals": [],
            "habits": []
        }
        
        for memory in memories[:MAX_CONTEXT_MEMORIES]:
            meta = memory.get("meta", {})
            memory_type = meta.get("type", "fact")
            value = memory.get("text", "") or memory.get("value", "")
            
            if value and memory_type in categories:
                categories[memory_type + "s"].append(value)
        
        # Remove empty categories
        structured = {k: v for k, v in categories.items() if v}
        
        return structured
        
    except Exception as e:
        logger.error(f"Error building structured context: {e}")
        return {}

def format_structured_context(structured: Dict[str, Any]) -> str:
    """
    Format structured context into readable string
    
    Args:
        structured: Structured context from build_structured_context
        
    Returns:
        Formatted context string
    """
    if not structured:
        return ""
    
    context_parts = ["IMPORTANT USER FACTS:\n"]
    
    category_names = {
        "preferences": "User Preferences",
        "facts": "Personal Facts",
        "constraints": "Important Constraints",
        "goals": "Goals & Objectives",
        "habits": "Habits & Routines"
    }
    
    for category, items in structured.items():
        if items:
            context_parts.append(f"\n{category_names.get(category, category)}:")
            for item in items:
                context_parts.append(f"  • {item}")
    
    context_parts.append("\n\nUse these facts naturally when relevant to the conversation.")
    
    return "\n".join(context_parts)
