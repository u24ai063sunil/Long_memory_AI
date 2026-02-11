from fastapi import FastAPI
from pydantic import BaseModel

from backend.utils.session import get_turn
from backend.llm.extractor import extract_memory
from backend.memory.schema import Memory
from backend.memory.add_memory import store_memory
from backend.memory.retrieve import retrieve_memories
from backend.memory.rank import rank_memories
from backend.llm.context_builder import build_context
from backend.llm.generator import generate_reply

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


@app.post("/chat")
def chat(req: ChatRequest):

    used_memories = []

    try:
        # ---------------- TURN COUNTER ----------------
        turn = get_turn(req.session_id)

        # ---------------- MEMORY EXTRACTION ----------------
        extracted = None
        try:
            extracted = extract_memory(req.message)
        except Exception as e:
            print("Extractor crash:", e)

        # ---------------- MEMORY STORE ----------------
        if extracted and isinstance(extracted, dict):
            try:
                memory = Memory(
                    session_id=req.session_id,
                    type=extracted.get("type", "fact"),
                    key=extracted.get("key", "general"),
                    value=extracted.get("value", ""),
                    confidence=float(extracted.get("confidence", 0.7)),
                    source_turn=turn,
                    last_used_turn=turn
                )
                store_memory(memory)
            except Exception as e:
                print("Memory storage error:", e)

        # ---------------- MEMORY RETRIEVAL ----------------
        memories = []
        try:
            memories = retrieve_memories(req.session_id, req.message) or []
        except Exception as e:
            print("Retrieval error:", e)

        # ---------------- MEMORY RANKING ----------------
        try:
            memories = rank_memories(memories, turn) or []
        except Exception as e:
            print("Ranking error:", e)

        used_memories = memories

        # ---------------- CONTEXT BUILD ----------------
        context = ""
        try:
            context = build_context(memories)
        except Exception as e:
            print("Context error:", e)

        # ---------------- RESPONSE GENERATION ----------------
        try:
            reply = generate_reply(req.message, context)
        except Exception as e:
            print("Generator error:", e)
            reply = "I’m having trouble answering right now, but I remember your preferences."

        return {
            "reply": reply,
            "used_memory": used_memories
        }

    except Exception as e:
        print("FATAL SERVER ERROR:", e)
        return {
            "reply": "System recovered from an internal error.",
            "used_memory": []
        }
