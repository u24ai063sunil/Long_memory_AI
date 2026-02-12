from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from utils.session import get_turn
from llm.extractor import extract_memory
from memory.schema import Memory
from memory.add_memory import store_memory_async
from memory.retrieve import retrieve_memories
from memory.rank import rank_memories
from llm.context_builder import build_context
from llm.generator import generate_reply
from reflection.generate_reflection import generate_reflections


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------------------------------------------------------
# BACKGROUND MEMORY PIPELINE
# ---------------------------------------------------------
def memory_pipeline(session_id, message, turn):

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

    # Reflection trigger
    if turn % 5 == 0:
        generate_reflections(session_id, turn)


# ---------------------------------------------------------
# CHAT ENDPOINT
# ---------------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest, bg: BackgroundTasks):

    turn = get_turn(req.session_id)

    # ---------- RETRIEVE ----------
    memories = retrieve_memories(req.session_id, req.message)

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