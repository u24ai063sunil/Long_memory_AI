import os
from dotenv import load_dotenv
from groq import Groq

from backend.memory.retrieve import retrieve_memories
from backend.memory.schema import Memory
from backend.memory.add_memory import store_memory
from backend.utils.session import get_turn

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


REFLECTION_PROMPT = """
You are a cognitive reflection engine for a personal AI assistant.

You are given a set of USER memories.

Your job is to generate HIGH-LEVEL INSIGHTS about the user.

Do NOT repeat memories.
Do NOT summarize.
Do NOT invent facts.

Only infer personality traits, behavioral patterns, or life priorities.

Return 3 reflections in JSON list format:

[
  "reflection 1",
  "reflection 2",
  "reflection 3"
]
"""


def build_memory_block(memories):
    """Convert memories into numbered text block."""

    lines = []

    for i, m in enumerate(memories, 1):
        text = m.get("text", "")
        if text:
            lines.append(f"{i}. {text}")

    return "\n".join(lines)


def generate_reflections(session_id: str, trigger_turn: int):

    # ---------- Safety ----------
    if not api_key:
        return []

    try:
        # ---------- Fetch recent memories ----------
        memories = retrieve_memories(
            session_id=session_id,
            query="user personal information",
            k=15
        )

        if not memories:
            return []

        memory_block = build_memory_block(memories)

        prompt = f"""
User Memories:

{memory_block}

Generate reflections.
"""

        # ---------- LLM Call ----------
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": REFLECTION_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=200,
        )

        if not response or not response.choices:
            return []

        content = response.choices[0].message.content

        if not content:
            return []

        # ---------- Parse reflections ----------
        import json
        reflections = json.loads(content)

        stored_ids = []

        for r in reflections:

            memory = Memory(
                session_id=session_id,
                type="reflection",
                key="user_insight",
                value=r,
                confidence=0.9,
                source_turn=trigger_turn,
                last_used_turn=trigger_turn
            )

            memory_id = store_memory(memory)
            stored_ids.append(memory_id)

        return stored_ids

    except Exception as e:
        print("Reflection generation error:", e)
        return []