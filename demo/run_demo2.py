import requests
import time

URL = "http://127.0.0.1:8000/chat"
SESSION = "multi_memory_demo"


def send(msg):
    print(f"\nUSER: {msg}")

    r = requests.post(
        URL,
        json={"session_id": SESSION, "message": msg},
        timeout=60
    )

    try:
        data = r.json()
    except:
        print("SERVER ERROR:")
        print(r.text)
        return

    print(f"ASSISTANT: {data['reply']}")

    if data.get("used_memory"):
        print("\n[Memory Used By System]")
        for m in data["used_memory"]:
            print(" ->", m["text"])


print("=====================================")
print(" MULTI-MEMORY LONG TERM DEMO")
print("=====================================")

# -------- MEMORY CREATION PHASE --------
print("\n--- Storing memories ---")

send("My preferred call time is after 11 AM.")
time.sleep(2)

send("I am vegetarian and I don't eat eggs.")
time.sleep(2)

send("I am working on a machine learning hackathon project.")
time.sleep(2)


# -------- DISTRACTION CONVERSATION --------
print("\n--- Irrelevant conversation ---")

small_talk = [
    "Tell me a joke",
    "Explain gravity",
    "What is 57 * 89?",
    "Write a short poem about space",
    "How do airplanes fly?",
]

for msg in small_talk:
    send(msg)
    time.sleep(1.5)


# -------- MEMORY RECALL TESTS --------
print("\n=====================================")
print(" MEMORY RECALL TESTS")
print("=====================================")

# Test 1 — schedule preference
print("\n[TEST 1: Schedule Recall]")
send("When should you call me?")

time.sleep(2)

# Test 2 — dietary constraint
print("\n[TEST 2: Dietary Recall]")
send("Suggest a breakfast for me.")

time.sleep(2)

# Test 3 — project awareness
print("\n[TEST 3: Work Context Recall]")
send("What kind of project am I doing?")

print("\n=====================================")
print(" DEMO COMPLETE")
print("=====================================")
