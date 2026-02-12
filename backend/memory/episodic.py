from backend.memory.retrieve import retrieve_memories
from backend.memory.add_memory import store_memory_async
from backend.memory.schema import Memory


def summarize_episode(session_id, turn):

    memories = retrieve_memories(session_id, "", k=20)

    if len(memories) < 10:
        return

    summary_text = "User conversation pattern summary."

    memory = Memory(
        session_id=session_id,
        type="episodic_summary",
        key=f"episode_{turn}",
        value=summary_text,
        confidence=0.6,
        source_turn=turn,
        last_used_turn=turn
    )

    store_memory_async(memory)

    print("📦 Episodic summary stored")