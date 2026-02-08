import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are a memory extraction engine.

Extract ONLY long-term useful user information.

Store ONLY if the message contains:
- preferences
- personal facts
- constraints
- commitments
- instructions

Return STRICT JSON ONLY.
No explanation.
No markdown.
No extra text.

If nothing important → return: null

JSON FORMAT:
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
