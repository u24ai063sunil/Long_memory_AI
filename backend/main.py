from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # Local dev
        "https://memory-chat-ui.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import custom modules with error handling
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
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("App will run but /chat endpoint may not work")

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------------------------------------------------------
# BACKGROUND MEMORY PIPELINE
# ---------------------------------------------------------
def memory_pipeline(session_id, message, turn):
    """Background task to extract and store memories"""
    try:
        extracted = extract_memory(message)

        if not extracted or not isinstance(extracted, dict):
            return

        memory = Memory(
            session_id=session_id,
            type=extracted.get("type", "fact"),
            key=extracted.get("key", "general"),
            value=extracted.get("value", ""),
            confidence=float(extracted.get("confidence", 0.7)),
            source_turn=turn,
            last_used_turn=turn
        )

        store_memory_async(memory)

        # Reflection trigger every 5 turns
        if turn % 5 == 0:
            generate_reflections(session_id, turn)
            
    except Exception as e:
        logger.error(f"Error in memory_pipeline: {e}")


@app.get("/")
def health():
    """Health check endpoint"""
    logger.info("Health check called")
    return {"status": "alive", "message": "Server is running"}


# ---------------------------------------------------------
# CHAT ENDPOINT
# ---------------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest, bg: BackgroundTasks):
    """Main chat endpoint with memory retrieval and storage"""
    try:
        logger.info(f"Chat request from session: {req.session_id}")
        
        # Get turn number
        turn = get_turn(req.session_id)

        # ---------- RETRIEVE ----------
        memories = retrieve_memories(req.session_id, req.message)
        logger.info(f"Retrieved {len(memories)} memories")

        # ---------- RANK ----------
        memories = rank_memories(memories, turn)

        # ---------- CONTEXT ----------
        context = build_context(memories)

        # ---------- GENERATE ----------
        reply = generate_reply(req.message, context)

        # ---------- ASYNC MEMORY ----------
        bg.add_task(memory_pipeline, req.session_id, req.message, turn)

        return {
            "reply": reply,
            "used_memory": memories
        }
        
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}", exc_info=True)
        return {
            "reply": "I apologize, but I encountered an error processing your request.",
            "error": str(e),
            "used_memory": []
        }


if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"🚀 Starting server on port {port}")
        
        # Run uvicorn server
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)