import requests
import time
import uuid

BASE_URL = "http://127.0.0.1:8000/chat"
SESSION_ID = "lifestyle_user_" + str(uuid.uuid4())

print("=====================================")
print(" REAL LIFE PERSONAL ASSISTANT DEMO")
print("=====================================")

def send(msg):
    print("\nUSER:", msg)

    try:
        r = requests.post(
            BASE_URL,
            json={"session_id": SESSION_ID, "message": msg},
            timeout=60
        )

        data = r.json()
        print("ASSISTANT:", data["reply"])

        if data.get("used_memory"):
            print("\n[Memory Used]")
            for m in data["used_memory"]:
                print(" ->", m.get("text"))

    except Exception as e:
        print("Error:", e)

    time.sleep(1.2)


conversation = [

# ---- casual start ----
"Hi there",
"How was your day?",
"Tell me something interesting",
"Recommend a movie genre",
"Write a short quote about life",

# ---- memory 1 (food preference) ----
"I don't drink coffee, I only drink tea.",

"What is insomnia?",
"Give me a relaxing activity idea",
"Tell me a joke",

# ---- memory 2 (work life) ----
"I work as a graphic designer.",

"Suggest a creative hobby",
"What is color theory?",
"Give me a productivity tip",

# ---- memory 3 (schedule) ----
"I usually start working at 10:30 in the morning.",

"Explain burnout",
"How to stay focused at work?",
"Give me a motivational line",

# ---- memory 4 (health constraint) ----
"I have lactose intolerance.",

"Suggest a dessert idea",
"How to improve sleep quality?",
"Tell me a random fact",

# ---- memory 5 (location) ----
"I recently moved to Pune.",

"What are good indoor plants?",
"Explain mindfulness",
"Give me a weekend activity idea",

# ---- memory 6 (communication preference) ----
"Please keep responses concise.",

"Explain meditation simply",
"Tell a short story",
"Give me a quick tip to relax",

# ---- memory 7 (habit) ----
"I go for a walk every evening around 7 PM.",

"What is anxiety?",
"How to manage stress?",
"Recommend a podcast topic",

# ---- memory 8 (diet) ----
"I avoid spicy food.",

"Suggest a dinner idea",
"What are calming colors?",
"Give me a positive affirmation",

# ---- memory 9 (allergy) ----
"I am allergic to cats.",

"What pet is low maintenance?",
"Tell me a fun fact",
"How to decorate a small room?",

# ---- memory 10 (goal) ----
"I want to start freelancing next year.",

"Explain freelancing basics",
"How to find clients?",
"Give career advice",

# ---- FINAL MEMORY RECALL ----
"What beverage should you suggest me in the morning?",
"What food should I avoid?",
"Where do I live now?",
"What is my job?",
"When am I usually free for a walk?",
"Do I have any health restrictions?"
]

for msg in conversation:
    send(msg)

print("\n=====================================")
print(" DEMO COMPLETE")
print("=====================================")
