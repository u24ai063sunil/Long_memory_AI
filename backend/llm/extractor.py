import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
# Lazily initialize Groq client; protect import-time initialization
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print("Warning: failed to initialize Groq client:", e)
        client = None

# SYSTEM_PROMPT = """
# You are a long-term memory extraction engine.

# You store ONLY stable, personal information about the USER.

# Store memories only if the message reveals something about the user's life, identity, or future interactions.

# VALID memories include:
# - preferences (likes/dislikes, schedule)
# - personal facts (job, studies, project, hobbies)
# - constraints (diet, availability)
# - commitments (plans or goals)
# - assistant instructions about how to interact with the user

# IMPORTANT:
# Projects, education, and ongoing work MUST be stored.

# DO NOT STORE:
# - questions about general knowledge
# - math problems
# - explanations
# - definitions
# - trivia
# - educational questions
# - anything about physics, history, science, weather, or facts about the world

# If the user is asking a question to learn information → return null.

# If the user is telling something about themselves → store it.

# Return STRICT JSON only.
# No explanation.

# If nothing important → return: null

# FORMAT:
# {
# "type": "preference | fact | constraint | commitment | instruction",
# "key": "short_identifier",
# "value": "important information",
# "confidence": 0.0-1.0
# }
# """
SYSTEM_PROMPT = """
You are a cognitive long-term memory extraction system for a personal AI assistant.

Your job is to decide whether the user's message contains information worth remembering about the USER — not the conversation.

You DO NOT summarize conversations.
You DO NOT store knowledge.
You DO NOT store questions.

You only store stable, reusable facts about the user.

---

## WHAT QUALIFIES AS A MEMORY

Store ONLY persistent user information:

1. Personal preferences
   (food choices, response style, UI preferences, communication preferences)
   Example:
   "I like dark mode"
   "I prefer short answers"

2. Personal facts / identity
   (location, occupation, ongoing project, student status)
   Example:
   "I live in Surat"
   "I am preparing for GATE"
   "I am working on a hackathon project"

3. Constraints & health
   (allergies, dietary restrictions, schedule limits)
   Example:
   "I am allergic to peanuts"
   "I am vegetarian"
   "Call me after 11 AM"

4. Long-term habits or routines
   Example:
   "I wake up at 9 AM"
   "I sleep at 2 AM"

5. Long-term goals
   Example:
   "I want to become a data scientist"
   "I am studying machine learning"

---

## WHAT MUST NEVER BE STORED

DO NOT STORE:

• questions
• general knowledge discussions
• explanations
• educational topics
• one-time tasks
• temporary plans
• assistant responses
• anything the assistant said
• anything inferred (only explicit user statements)

Examples NOT to store:
"Explain WiFi"
"What is gravity?"
"Tell me a joke"
"Airplanes fly using lift"
"We discussed blockchain"
"Help me solve this problem"

If the message is not stable user information → return null.

---

OUTPUT FORMAT (STRICT JSON ONLY)

Return exactly:

{
"type": "preference | fact | constraint | habit | goal",
"key": "short_machine_readable_identifier",
"value": "the actual user information in natural language",
"confidence": 0.0-1.0
}

Rules:

* No markdown
* No explanation
* No extra text
* No code block
* Only JSON or null
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

    if len(message.split()) < 2:
        return None
    # no key configured or client failed to initialize
    if not api_key or not client:
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
