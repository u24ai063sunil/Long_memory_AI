import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def generate_reply(user_message, context):

    system_prompt = f"""
You are a helpful personal assistant.

You have access to long-term user information.

User facts:
{context}

When relevant, follow these facts while answering.
Give a clear and natural response.
"""

    # If key missing → don't crash
    if not api_key:
        return "The language model is not configured, but your memory system is working."

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=200,
        )

        # very important safety extraction
        if not chat_completion or not chat_completion.choices:
            return "I couldn't generate a response, but I received your message."

        message = chat_completion.choices[0].message.content

        if not message:
            return "I processed your request, but the model returned an empty answer."

        return message.strip()

    except Exception as e:
        print("Groq API error:", e)
        return "I'm temporarily unable to access my language model, but I remember your preferences."
