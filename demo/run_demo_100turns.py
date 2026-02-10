import requests
import time
import random

URL = "http://127.0.0.1:8000/chat"
SESSION = "stress_test_user"

def send(msg, delay=0.4):
    print(f"\nUSER: {msg}")

    try:
        r = requests.post(URL, json={"session_id": SESSION, "message": msg}, timeout=20)

        if r.status_code != 200:
            print("ASSISTANT: (Server error)", r.status_code)
            return

        data = r.json()

        print("ASSISTANT:", data["reply"][:250])

        if data.get("used_memory"):
            print("\n[Memory Used]")
            for m in data["used_memory"]:
                print(" ->", m["text"])

    except Exception as e:
        print("Connection error:", e)

    time.sleep(delay)


# ---------------------------

# MEMORY EVENTS (10 memories)

# ---------------------------

memory_events = {
3: "My preferred call time is after 11 AM.",
11: "I am vegetarian and I don't eat eggs.",
18: "I live in Surat.",
27: "I wake up at 9 AM daily.",
35: "I am preparing for GATE exam.",
46: "I like dark mode apps.",
55: "I am allergic to peanuts.",
63: "I prefer short answers.",
72: "I usually sleep at 2 AM.",
85: "I am working on an AI memory chatbot project."
}

# ---------------------------

# FILLER CONVERSATIONS

# ---------------------------

small_talk = [
"Tell me a joke",
"What is gravity?",
"Explain WiFi",
"What is 23 * 67?",
"Give a random fact",
"Write a poem",
"Explain machine learning",
"What is a black hole?",
"Explain blockchain",
"How do airplanes fly?"
]

print("=====================================")
print(" 100 TURN LONG-TERM MEMORY STRESS TEST")
print("=====================================")

time.sleep(1)

# ---------------------------

# 100 TURNS

# ---------------------------

for turn in range(1, 101):

# if this turn is a memory event
    if turn in memory_events:
        send(memory_events[turn])
    else:
        send(random.choice(small_talk))
    

# ---------------------------

# RECALL TEST

# ---------------------------

print("\n=====================================")
print(" FINAL MEMORY RECALL TEST")
print("=====================================")

time.sleep(2)

send("When should you call me?")
send("Suggest a breakfast for me.")
send("Do I have any allergies?")
send("What am I preparing for?")
send("What project am I working on?")
send("When do I sleep?")
