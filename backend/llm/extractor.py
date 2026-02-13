# import os
# import json
# import re
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=api_key)

# # SYSTEM_PROMPT = """
# # You are a long-term memory extraction engine.

# # You store ONLY stable, personal information about the USER.

# # Store memories only if the message reveals something about the user's life, identity, or future interactions.

# # VALID memories include:
# # - preferences (likes/dislikes, schedule)
# # - personal facts (job, studies, project, hobbies)
# # - constraints (diet, availability)
# # - commitments (plans or goals)
# # - assistant instructions about how to interact with the user

# # IMPORTANT:
# # Projects, education, and ongoing work MUST be stored.

# # DO NOT STORE:
# # - questions about general knowledge
# # - math problems
# # - explanations
# # - definitions
# # - trivia
# # - educational questions
# # - anything about physics, history, science, weather, or facts about the world

# # If the user is asking a question to learn information → return null.

# # If the user is telling something about themselves → store it.

# # Return STRICT JSON only.
# # No explanation.

# # If nothing important → return: null

# # FORMAT:
# # {
# # "type": "preference | fact | constraint | commitment | instruction",
# # "key": "short_identifier",
# # "value": "important information",
# # "confidence": 0.0-1.0
# # }
# # """
# SYSTEM_PROMPT = """
# You are a cognitive long-term memory extraction system for a personal AI assistant.

# Your job is to decide whether the user's message contains information worth remembering about the USER — not the conversation.

# You DO NOT summarize conversations.
# You DO NOT store knowledge.
# You DO NOT store questions.

# You only store stable, reusable facts about the user.

# ---

# ## WHAT QUALIFIES AS A MEMORY

# Store ONLY persistent user information:

# 1. Personal preferences
#    (food choices, response style, UI preferences, communication preferences)
#    Example:
#    "I like dark mode"
#    "I prefer short answers"

# 2. Personal facts / identity
#    (location, occupation, ongoing project, student status)
#    Example:
#    "I live in Surat"
#    "I am preparing for GATE"
#    "I am working on a hackathon project"

# 3. Constraints & health
#    (allergies, dietary restrictions, schedule limits)
#    Example:
#    "I am allergic to peanuts"
#    "I am vegetarian"
#    "Call me after 11 AM"

# 4. Long-term habits or routines
#    Example:
#    "I wake up at 9 AM"
#    "I sleep at 2 AM"

# 5. Long-term goals
#    Example:
#    "I want to become a data scientist"
#    "I am studying machine learning"

# ---

# ## WHAT MUST NEVER BE STORED

# DO NOT STORE:

# • questions
# • general knowledge discussions
# • explanations
# • educational topics
# • one-time tasks
# • temporary plans
# • assistant responses
# • anything the assistant said
# • anything inferred (only explicit user statements)

# Examples NOT to store:
# "Explain WiFi"
# "What is gravity?"
# "Tell me a joke"
# "Airplanes fly using lift"
# "We discussed blockchain"
# "Help me solve this problem"

# If the message is not stable user information → return null.

# ---

# OUTPUT FORMAT (STRICT JSON ONLY)

# Return exactly:

# {
# "type": "preference | fact | constraint | habit | goal",
# "key": "short_machine_readable_identifier",
# "value": "the actual user information in natural language",
# "confidence": 0.0-1.0
# }

# Rules:

# * No markdown
# * No explanation
# * No extra text
# * No code block
# * Only JSON or null
#   """



# def extract_json(text: str):
#     # remove markdown
#     text = re.sub(r"```json", "", text)
#     text = re.sub(r"```", "", text).strip()

#     # find JSON
#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     if not match:
#         return None

#     try:
#         return json.loads(match.group(0))
#     except Exception:
#         return None


# def extract_memory(message: str):
#     message = message.strip()

#     # Ignore conversational noise
#     if message.endswith("?"):
#         return None

#     if len(message.split()) < 4:
#         return None
#     # no key configured
#     if not api_key:
#         return None

#     try:
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": message}
#             ],
#             model="llama-3.1-8b-instant",
#             temperature=0,
#             max_tokens=200,
#         )

#         # ----- SAFE RESPONSE HANDLING -----
#         if not response:
#             return None

#         if not hasattr(response, "choices"):
#             return None

#         if len(response.choices) == 0:
#             return None

#         msg = response.choices[0].message

#         if not msg:
#             return None

#         text = msg.content

#         if not text:
#             return None

#         text = text.strip()

#         if text.lower() == "null":
#             return None

#         return extract_json(text)

#     except Exception as e:
#         print("Extractor error:", e)
#         return None
"""
Memory Extraction Module
Extracts long-term user memories from messages using LLM
"""

import os
import json
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from groq import Groq
from functools import lru_cache
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.warning("⚠️ GROQ_API_KEY not found. Memory extraction will be disabled.")

client = Groq(api_key=api_key) if api_key else None

# Model configuration
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
TEMPERATURE = float(os.getenv("EXTRACTION_TEMPERATURE", "0"))
MAX_TOKENS = int(os.getenv("EXTRACTION_MAX_TOKENS", "200"))

# ============================================
# SYSTEM PROMPT (IMPROVED)
# ============================================
SYSTEM_PROMPT = """You are a cognitive long-term memory extraction system for a personal AI assistant.

Your ONLY job is to identify and extract stable, reusable facts about the USER.

## CORE PRINCIPLE
Store information that will help the assistant provide better, more personalized responses in FUTURE conversations.

## ✅ WHAT TO STORE (Persistent User Information)

### 1. Personal Identity & Demographics
- Name, age, location
- Occupation, education level, field of study
- Role (student, professional, parent, etc.)

Examples:
✓ "I'm a software engineer"
✓ "I live in Mumbai"
✓ "I'm studying computer science"

### 2. Preferences & Likes/Dislikes
- Communication style preferences
- UI/UX preferences
- Food, hobbies, interests
- Working style

Examples:
✓ "I prefer concise answers"
✓ "I love dark chocolate"
✓ "I work better at night"

### 3. Constraints & Limitations
- Dietary restrictions, allergies
- Time constraints, availability
- Physical or health limitations
- Budget constraints

Examples:
✓ "I'm allergic to shellfish"
✓ "I'm available after 6 PM"
✓ "I have a limited budget"

### 4. Long-term Goals & Projects
- Career aspirations
- Learning objectives
- Ongoing projects
- Personal development goals

Examples:
✓ "I'm preparing for GATE exam"
✓ "I'm building an AI chatbot"
✓ "I want to learn Spanish"

### 5. Routines & Habits
- Daily schedules
- Work routines
- Regular activities

Examples:
✓ "I exercise every morning"
✓ "I study from 9 PM to 11 PM"
✓ "I take breaks every hour"

## ❌ WHAT NOT TO STORE

DO NOT store:
- ❌ Questions ("What is machine learning?")
- ❌ General knowledge requests ("Explain quantum physics")
- ❌ Temporary tasks ("Remind me to buy milk")
- ❌ Current conversation summaries
- ❌ One-time events ("I went to a party yesterday")
- ❌ Assistant's responses
- ❌ Facts about the world (not about the user)
- ❌ Greetings, small talk, acknowledgments

## CONFIDENCE SCORING

Assign confidence based on:
- 0.9-1.0: Explicit, clear statement ("I am a vegetarian")
- 0.7-0.8: Strong implication ("I don't eat meat")
- 0.5-0.6: Weak implication or ambiguous
- Below 0.5: Don't store

## OUTPUT FORMAT

Return ONLY valid JSON or null. No markdown, no explanation.

```json
{
  "type": "preference | fact | constraint | habit | goal",
  "key": "short_identifier_in_snake_case",
  "value": "Clear, natural language description",
  "confidence": 0.0-1.0
}
```

### Key Guidelines:
- Keep "key" short, descriptive, machine-readable (e.g., "preferred_language", "dietary_restriction")
- Keep "value" natural, human-readable (e.g., "The user prefers Python", "The user is vegetarian")
- Use present tense, third person

## EXAMPLES

Input: "I'm a vegetarian"
Output: {"type": "constraint", "key": "dietary_restriction", "value": "The user is vegetarian", "confidence": 1.0}

Input: "I love working late at night"
Output: {"type": "habit", "key": "work_schedule", "value": "The user prefers working late at night", "confidence": 0.9}

Input: "What is Python?"
Output: null

Input: "Explain machine learning"
Output: null

Input: "I'm preparing for my final exams"
Output: {"type": "goal", "key": "current_focus", "value": "The user is preparing for final exams", "confidence": 0.9}

Remember: If in doubt, return null. Better to miss a memory than store irrelevant information.
"""

# ============================================
# HELPER FUNCTIONS
# ============================================
def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from LLM response, handling markdown and other formatting
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Parsed JSON dict or None
    """
    if not text:
        return None
    
    # Remove markdown code blocks
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    
    # Check for explicit null
    if text.lower() in ["null", "none", "n/a"]:
        return None
    
    # Find JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    
    try:
        parsed = json.loads(match.group(0))
        
        # Validate required fields
        required_fields = ["type", "key", "value", "confidence"]
        if not all(field in parsed for field in required_fields):
            logger.warning(f"Extracted JSON missing required fields: {parsed}")
            return None
        
        # Validate confidence range
        confidence = float(parsed.get("confidence", 0))
        if not 0 <= confidence <= 1:
            logger.warning(f"Invalid confidence value: {confidence}")
            return None
        
        # Validate types
        valid_types = ["preference", "fact", "constraint", "habit", "goal"]
        if parsed.get("type") not in valid_types:
            logger.warning(f"Invalid memory type: {parsed.get('type')}")
            return None
        
        return parsed
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in extract_json: {e}")
        return None

def should_skip_extraction(message: str) -> bool:
    """
    Quick heuristic check to skip obviously non-memorable messages
    
    Args:
        message: User message
        
    Returns:
        True if should skip extraction
    """
    message = message.strip().lower()
    
    # Skip very short messages
    if len(message.split()) < 4:
        return True
    
    # Skip questions (high probability)
    if message.endswith("?"):
        return True
    
    # Skip common non-memorable patterns
    skip_patterns = [
        r"^(hi|hello|hey|thanks|thank you|ok|okay|yes|no|sure)\b",
        r"^(what|how|when|where|why|who|which)\b",
        r"^(explain|tell me|show me|define|describe)\b",
        r"^(can you|could you|would you|will you)\b",
    ]
    
    for pattern in skip_patterns:
        if re.match(pattern, message):
            return True
    
    return False

# ============================================
# MAIN EXTRACTION FUNCTION
# ============================================
def extract_memory(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract memory from user message using LLM
    
    Args:
        message: User message
        
    Returns:
        Dictionary with extracted memory or None
    """
    try:
        message = message.strip()
        
        # Quick validation
        if not message:
            return None
        
        # Heuristic pre-filtering
        if should_skip_extraction(message):
            logger.debug(f"Skipping extraction for: {message[:50]}...")
            return None
        
        # Check API key
        if not api_key or not client:
            logger.warning("Memory extraction disabled: No API key")
            return None
        
        # Call LLM
        logger.debug(f"Extracting memory from: {message[:100]}...")
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        
        # Validate response
        if not response or not hasattr(response, "choices") or len(response.choices) == 0:
            logger.warning("Invalid LLM response structure")
            return None
        
        msg = response.choices[0].message
        if not msg or not hasattr(msg, "content"):
            logger.warning("No content in LLM response")
            return None
        
        text = msg.content
        if not text:
            return None
        
        text = text.strip()
        
        # Parse and validate
        extracted = extract_json(text)
        
        if extracted:
            logger.info(f"✅ Memory extracted: {extracted['key']} (confidence: {extracted['confidence']})")
        else:
            logger.debug("No memory extracted from message")
        
        return extracted
        
    except Exception as e:
        logger.error(f"Extractor error: {e}", exc_info=True)
        return None

# ============================================
# BATCH EXTRACTION (OPTIONAL)
# ============================================
def extract_memories_batch(messages: list[str]) -> list[Optional[Dict[str, Any]]]:
    """
    Extract memories from multiple messages
    Useful for processing conversation history
    
    Args:
        messages: List of user messages
        
    Returns:
        List of extracted memories (with None for non-memorable messages)
    """
    return [extract_memory(msg) for msg in messages]
