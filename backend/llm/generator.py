# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=api_key)


# def generate_reply(user_message, context):

#     system_prompt = f"""
# You are a helpful personal assistant.

# You have access to long-term user information.

# User facts:
# {context}

# When relevant, follow these facts while answering.
# Give a clear and natural response.
# """

#     # If key missing → don't crash
#     if not api_key:
#         return "The language model is not configured, but your memory system is working."

#     try:
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_message}
#             ],
#             model="llama-3.1-8b-instant",
#             temperature=0.5,
#             max_tokens=200,
#         )

#         # very important safety extraction
#         if not chat_completion or not chat_completion.choices:
#             return "I couldn't generate a response, but I received your message."

#         message = chat_completion.choices[0].message.content

#         if not message:
#             return "I processed your request, but the model returned an empty answer."

#         return message.strip()

#     except Exception as e:
#         print("Groq API error:", e)
#         return "I'm temporarily unable to access my language model, but I remember your preferences."
"""
Response Generator Module
Generates contextual responses using LLM with user memory
"""

import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.warning("⚠️ GROQ_API_KEY not found. Response generation will use fallback.")

client = Groq(api_key=api_key) if api_key else None

# Model configuration
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("GENERATION_MAX_TOKENS", "500"))

# ============================================
# SYSTEM PROMPT TEMPLATE
# ============================================
SYSTEM_PROMPT_TEMPLATE = """You are a helpful, intelligent personal AI assistant with long-term memory.

You have access to important information about the user from previous conversations.

## USER CONTEXT
{context}

## GUIDELINES

1. **Use Memory Naturally**
   - Reference user facts when relevant
   - Don't awkwardly force memory into every response
   - If memory isn't relevant, ignore it

2. **Be Conversational**
   - Keep responses natural and engaging
   - Match the user's tone and style
   - Be concise but complete

3. **Be Helpful**
   - Answer questions directly
   - Provide actionable advice
   - Offer follow-up suggestions when appropriate

4. **Respect Preferences**
   - Follow any communication preferences mentioned in the context
   - Adapt response length and style to user preferences
   - Honor any constraints or limitations

5. **Privacy & Trust**
   - Never reveal that you're storing information unless asked
   - Treat all user information as confidential
   - Be honest about your capabilities

Remember: You're having a conversation with someone you know, not a stranger.
"""

FALLBACK_SYSTEM_PROMPT = """You are a helpful AI assistant.
Provide clear, accurate, and concise responses to user questions.
Be friendly, professional, and respectful."""

# ============================================
# HELPER FUNCTIONS
# ============================================
def format_context(context: str) -> str:
    """
    Format context for better readability in the prompt
    
    Args:
        context: Raw context string from memory
        
    Returns:
        Formatted context string
    """
    if not context or context.strip() == "":
        return "No previous context available."
    
    # If context is well-formatted, return as is
    if context.startswith("IMPORTANT USER FACTS"):
        return context
    
    # Otherwise, wrap it nicely
    return f"IMPORTANT USER FACTS:\n{context}"

def build_system_prompt(context: Optional[str]) -> str:
    """
    Build complete system prompt with context
    
    Args:
        context: User memory context
        
    Returns:
        Complete system prompt
    """
    if not context or context.strip() == "":
        formatted_context = "No previous context available. This is a new conversation."
    else:
        formatted_context = format_context(context)
    
    return SYSTEM_PROMPT_TEMPLATE.format(context=formatted_context)

# ============================================
# MAIN GENERATION FUNCTION
# ============================================
def generate_reply(user_message: str, context: Optional[str] = None) -> str:
    """
    Generate AI response using user message and memory context
    
    Args:
        user_message: Current user message
        context: Relevant user memories and context
        
    Returns:
        Generated response string
    """
    try:
        # Validate input
        if not user_message or not user_message.strip():
            logger.warning("Empty user message provided")
            return "I didn't receive your message. Could you please try again?"
        
        user_message = user_message.strip()
        
        # Check API availability
        if not api_key or not client:
            logger.warning("LLM not configured, using fallback")
            return (
                "I'm currently unable to access my language model, "
                "but I'm still learning about you for future conversations. "
                "Please try again in a moment."
            )
        
        # Build system prompt
        system_prompt = build_system_prompt(context)
        
        logger.debug(f"Generating response for: {user_message[:100]}...")
        if context:
            logger.debug(f"Using context: {len(context)} characters")
        
        # Call LLM
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        
        # Validate response
        if not response or not response.choices or len(response.choices) == 0:
            logger.error("Invalid LLM response structure")
            return "I'm having trouble generating a response. Please try again."
        
        message = response.choices[0].message.content
        
        if not message or not message.strip():
            logger.error("Empty response from LLM")
            return "I processed your request, but couldn't generate a proper response. Please try again."
        
        reply = message.strip()
        logger.info(f"✅ Generated response: {len(reply)} characters")
        
        return reply
        
    except Exception as e:
        logger.error(f"Error in generate_reply: {e}", exc_info=True)
        
        # User-friendly error message
        return (
            "I apologize, but I'm experiencing technical difficulties. "
            "Your message was received and I'm still learning from our conversation. "
            "Please try again in a moment."
        )

# ============================================
# STREAMING GENERATION (OPTIONAL)
# ============================================
def generate_reply_stream(user_message: str, context: Optional[str] = None):
    """
    Generate streaming response (for real-time UI updates)
    
    Args:
        user_message: Current user message
        context: Relevant user memories and context
        
    Yields:
        Response chunks as they're generated
    """
    try:
        if not api_key or not client:
            yield "I'm currently unable to access my language model."
            return
        
        system_prompt = build_system_prompt(context)
        
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"Error in streaming generation: {e}")
        yield "I encountered an error while generating the response."

# ============================================
# RESPONSE POST-PROCESSING (OPTIONAL)
# ============================================
def post_process_response(response: str) -> str:
    """
    Clean and format the generated response
    
    Args:
        response: Raw LLM response
        
    Returns:
        Cleaned response
    """
    # Remove excessive whitespace
    response = " ".join(response.split())
    
    # Remove any system artifacts
    response = response.replace("```", "")
    
    # Ensure proper ending punctuation
    if response and not response[-1] in ".!?":
        response += "."
    
    return response