# from fastapi import FastAPI, BackgroundTasks
# from pydantic import BaseModel
# import logging
# import sys
# import os

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     stream=sys.stdout
# )
# logger = logging.getLogger(__name__)

# app = FastAPI()

# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",           # Local dev
#         "https://memory-chat-ui.vercel.app"  # Production
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Import custom modules with error handling
# try:
#     from utils.session import get_turn
#     from llm.extractor import extract_memory
#     from memory.schema import Memory
#     from memory.add_memory import store_memory_async
#     from memory.retrieve import retrieve_memories
#     from memory.rank import rank_memories
#     from llm.context_builder import build_context
#     from llm.generator import generate_reply
#     from reflection.generate_reflection import generate_reflections
#     logger.info("✅ All modules imported successfully")
# except ImportError as e:
#     logger.error(f"❌ Import error: {e}")
#     logger.error("App will run but /chat endpoint may not work")

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# # ---------------------------------------------------------
# # BACKGROUND MEMORY PIPELINE
# # ---------------------------------------------------------
# def memory_pipeline(session_id, message, turn):
#     """Background task to extract and store memories"""
#     try:
#         extracted = extract_memory(message)

#         if not extracted or not isinstance(extracted, dict):
#             return

#         memory = Memory(
#             session_id=session_id,
#             type=extracted.get("type", "fact"),
#             key=extracted.get("key", "general"),
#             value=extracted.get("value", ""),
#             confidence=float(extracted.get("confidence", 0.7)),
#             source_turn=turn,
#             last_used_turn=turn
#         )

#         store_memory_async(memory)

#         # Reflection trigger every 5 turns
#         if turn % 5 == 0:
#             generate_reflections(session_id, turn)
            
#     except Exception as e:
#         logger.error(f"Error in memory_pipeline: {e}")


# @app.get("/")
# def health():
#     """Health check endpoint"""
#     logger.info("Health check called")
#     return {"status": "alive", "message": "Server is running"}


# # ---------------------------------------------------------
# # CHAT ENDPOINT
# # ---------------------------------------------------------
# @app.post("/chat")
# def chat(req: ChatRequest, bg: BackgroundTasks):
#     """Main chat endpoint with memory retrieval and storage"""
#     try:
#         logger.info(f"Chat request from session: {req.session_id}")
        
#         # Get turn number
#         turn = get_turn(req.session_id)

#         # ---------- RETRIEVE ----------
#         memories = retrieve_memories(req.session_id, req.message)
#         logger.info(f"Retrieved {len(memories)} memories")

#         # ---------- RANK ----------
#         memories = rank_memories(memories, turn)

#         # ---------- CONTEXT ----------
#         context = build_context(memories)

#         # ---------- GENERATE ----------
#         reply = generate_reply(req.message, context)

#         # ---------- ASYNC MEMORY ----------
#         bg.add_task(memory_pipeline, req.session_id, req.message, turn)

#         return {
#             "reply": reply,
#             "used_memory": memories
#         }
        
#     except Exception as e:
#         logger.error(f"Error in /chat endpoint: {e}", exc_info=True)
#         return {
#             "reply": "I apologize, but I encountered an error processing your request.",
#             "error": str(e),
#             "used_memory": []
#         }


# if __name__ == "__main__":
#     try:
#         port = int(os.environ.get("PORT", 8000))
#         logger.info(f"🚀 Starting server on port {port}")
        
#         # Run uvicorn server
#         import uvicorn
#         uvicorn.run(
#             app, 
#             host="0.0.0.0", 
#             port=port,
#             log_level="info"
#         )
#     except Exception as e:
#         logger.error(f"❌ Failed to start server: {e}")
#         sys.exit(1)
"""
FastAPI Memory Chat Backend
Main application entry point with chat endpoint and memory pipeline
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import logging
import sys
import os
from typing import Optional, List, Dict, Any

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log') if os.environ.get('LOG_TO_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# FASTAPI APP INITIALIZATION
# ============================================
app = FastAPI(
    title="Memory Chat API",
    description="AI chat assistant with long-term memory",
    version="1.0.0"
)

# ============================================
# CORS MIDDLEWARE
# ============================================
# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",  # Environment variable name
    "http://localhost:5173,https://memory-chat-ui.vercel.app"  # Default value
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# IMPORT CUSTOM MODULES
# ============================================
try:
    from utils.session import get_turn
    from llm.extractor import extract_memory
    from memory.schema import Memory
    from memory.add_memory import store_memory_async
    from memory.retrieve import retrieve_memories
    from memory.rank import rank_memories
    from llm.context_builder import build_context
    from llm.generator import generate_reply
    from reflection.generate_reflection import generate_reflections
    
    logger.info("✅ All modules imported successfully")
    MODULES_LOADED = True
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("Some endpoints may not work properly")
    MODULES_LOADED = False

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================
class ChatRequest(BaseModel):
    """Chat request model with validation"""
    session_id: str = Field(..., min_length=1, max_length=100, description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """Ensure session_id is alphanumeric with allowed special chars"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('session_id must be alphanumeric with optional hyphens/underscores')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Clean and validate message"""
        return v.strip()

class ChatResponse(BaseModel):
    """Chat response model"""
    reply: str
    used_memory: List[Dict[str, Any]] = []
    turn: Optional[int] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    modules_loaded: bool
    version: str

# ============================================
# BACKGROUND TASKS
# ============================================
def memory_pipeline(session_id: str, message: str, turn: int) -> None:
    """
    Background task to extract and store memories
    
    Args:
        session_id: User session identifier
        message: User message
        turn: Current conversation turn number
    """
    try:
        logger.info(f"Starting memory pipeline for session {session_id}, turn {turn}")
        
        # Extract memory from message
        extracted = extract_memory(message)

        # Validate extraction result
        if not extracted or not isinstance(extracted, dict):
            logger.debug(f"No memory extracted from message: {message[:50]}...")
            return

        # Ensure required fields
        if not extracted.get("value"):
            logger.warning("Extracted memory missing 'value' field")
            return

        # Create memory object
        memory = Memory(
            session_id=session_id,
            type=extracted.get("type", "fact"),
            key=extracted.get("key", "general"),
            value=extracted.get("value", ""),
            confidence=float(extracted.get("confidence", 0.7)),
            source_turn=turn,
            last_used_turn=turn
        )

        # Store memory
        store_memory_async(memory)
        logger.info(f"Memory stored: {memory.key} = {memory.value[:50]}...")

        # Generate reflections every 5 turns
        if turn % 5 == 0:
            logger.info(f"Generating reflections at turn {turn}")
            generate_reflections(session_id, turn)
            
    except Exception as e:
        logger.error(f"Error in memory_pipeline: {e}", exc_info=True)

# ============================================
# ENDPOINTS
# ============================================
@app.get("/", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Health check endpoint
    Returns server status and module load state
    """
    logger.debug("Health check called")
    return HealthResponse(
        status="healthy" if MODULES_LOADED else "degraded",
        message="Server is running" if MODULES_LOADED else "Server running with module errors",
        modules_loaded=MODULES_LOADED,
        version="1.0.0"
    )

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, bg: BackgroundTasks) -> ChatResponse:
    """
    Main chat endpoint with memory retrieval and storage
    
    Args:
        req: Chat request with session_id and message
        bg: Background tasks manager
        
    Returns:
        ChatResponse with reply and used memories
    """
    try:
        logger.info(f"Chat request from session: {req.session_id}")
        logger.debug(f"Message: {req.message[:100]}...")
        
        # Check if modules are loaded
        if not MODULES_LOADED:
            raise HTTPException(
                status_code=503, 
                detail="Server modules not loaded properly"
            )
        
        # Get turn number
        turn = get_turn(req.session_id)
        logger.debug(f"Current turn: {turn}")

        # ---------- RETRIEVE MEMORIES ----------
        memories = retrieve_memories(req.session_id, req.message)
        logger.info(f"Retrieved {len(memories)} memories")

        # ---------- RANK MEMORIES ----------
        ranked_memories = rank_memories(memories, turn)
        logger.debug(f"Ranked {len(ranked_memories)} memories")

        # ---------- BUILD CONTEXT ----------
        context = build_context(ranked_memories)
        if context:
            logger.debug(f"Context built: {len(context)} characters")

        # ---------- GENERATE REPLY ----------
        reply = generate_reply(req.message, context)
        logger.info(f"Reply generated: {len(reply)} characters")

        # ---------- SCHEDULE BACKGROUND MEMORY EXTRACTION ----------
        bg.add_task(memory_pipeline, req.session_id, req.message, turn)

        return ChatResponse(
            reply=reply,
            used_memory=ranked_memories,
            turn=turn
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}", exc_info=True)
        
        # Return user-friendly error
        return ChatResponse(
            reply="I apologize, but I encountered an error processing your request. Please try again.",
            used_memory=[],
            error=str(e) if os.environ.get("DEBUG") else None
        )

# ============================================
# OPTIONAL: MEMORY MANAGEMENT ENDPOINTS
# ============================================
@app.get("/session/{session_id}/memories")
def get_session_memories(session_id: str, limit: int = 50):
    """
    Get all memories for a session (optional admin endpoint)
    """
    try:
        from memory.retrieve import get_all_memories
        memories = get_all_memories(session_id, limit=limit)
        return {
            "session_id": session_id,
            "count": len(memories),
            "memories": memories
        }
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}/memories")
def clear_session_memories(session_id: str):
    """
    Clear all memories for a session (optional admin endpoint)
    """
    try:
        from memory.json_store import clear_session
        clear_session(session_id)
        return {
            "status": "success",
            "message": f"Cleared memories for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Error clearing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SERVER STARTUP
# ============================================
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        reload = os.environ.get("RELOAD", "false").lower() == "true"
        
        logger.info(f"🚀 Starting server on {host}:{port}")
        logger.info(f"📝 Allowed origins: {ALLOWED_ORIGINS}")
        logger.info(f"🔄 Auto-reload: {reload}")
        
        # Run uvicorn server
        import uvicorn
        uvicorn.run(
            "main:app" if reload else app,
            host=host,
            port=port,
            log_level="info",
            reload=reload
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)