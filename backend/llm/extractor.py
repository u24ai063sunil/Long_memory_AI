import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are a long-term memory extraction engine.

You store ONLY stable, personal information about the USER.

Store memories only if the message reveals something about the user's life, identity, or future interactions.

VALID memories include:
- preferences (likes/dislikes, schedule)
- personal facts (job, studies, project, hobbies)
- constraints (diet, availability)
- commitments (plans or goals)
- assistant instructions about how to interact with the user

IMPORTANT:
Projects, education, and ongoing work MUST be stored.

DO NOT STORE:
- questions about general knowledge
- math problems
- explanations
- definitions
- trivia
- educational questions
- anything about physics, history, science, weather, or facts about the world

If the user is asking a question to learn information → return null.

If the user is telling something about themselves → store it.

Return STRICT JSON only.
No explanation.

If nothing important → return: null

FORMAT:
{
"type": "preference | fact | constraint | commitment | instruction",
"key": "short_identifier",
"value": "important information",
"confidence": 0.0-1.0
}
"""


def extract_json(text: str):
    # remove markdown
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text).strip()

    # find JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def extract_memory(message: str):
    message = message.strip()

    # Ignore conversational noise
    if message.endswith("?"):
        return None

    if len(message.split()) < 4:
        return None
    # no key configured
    if not api_key:
        return None

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=200,
        )

        # ----- SAFE RESPONSE HANDLING -----
        if not response:
            return None

        if not hasattr(response, "choices"):
            return None

        if len(response.choices) == 0:
            return None

        msg = response.choices[0].message

        if not msg:
            return None

        text = msg.content

        if not text:
            return None

        text = text.strip()

        if text.lower() == "null":
            return None

        return extract_json(text)

    except Exception as e:
        print("Extractor error:", e)
        return None
