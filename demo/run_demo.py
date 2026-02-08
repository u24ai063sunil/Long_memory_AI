import requests
import time

URL = "http://127.0.0.1:8000/chat"
SESSION = "judge_demo_user"


def wait_for_server():
    print("Checking server availability...")
    for _ in range(20):
        try:
            r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
            if r.status_code == 200:
                print("Server is ready!\n")
                return
        except:
            pass
        time.sleep(1)

    print("ERROR: Backend server is not running.")
    print("Please start with: uvicorn backend.main:app --reload")
    exit()


def send(msg):
    print(f"\nUSER: {msg}")

    try:
        r = requests.post(
            URL,
            json={"session_id": SESSION, "message": msg},
            timeout=60
        )

        # server crashed
        if r.status_code != 200:
            print("ASSISTANT: (Server returned error)")
            print("Status Code:", r.status_code)
            print(r.text)
            return

        try:
            data = r.json()
        except:
            print("ASSISTANT: (Invalid JSON response from server)")
            print(r.text)
            return

        print(f"ASSISTANT: {data.get('reply', '(no reply)')}")

        if data.get("used_memory"):
            print("\n[Memory Used By System]")
            for m in data["used_memory"]:
                print(" ->", m["text"])

    except requests.exceptions.Timeout:
        print("ASSISTANT: (Request timed out)")

    except requests.exceptions.ConnectionError:
        print("ASSISTANT: (Cannot connect to backend)")
        print("Did you start the server?")
        print("Run: uvicorn backend.main:app --reload")
        exit()


print("=====================================")
print(" LONG FORM MEMORY DEMO STARTING")
print("=====================================")

wait_for_server()
time.sleep(1)

# ---- Turn 1 (Important memory) ----
send("Hi, my preferred call time is after 11 AM.")

time.sleep(2)

# ---- Irrelevant conversations ----
small_talk = [
    "What is the weather today?",
    "Tell me a joke",
    "Who won the world cup 2011?",
    "Explain black holes in simple words",
    "What is 25 * 47?",
    "Give me a healthy breakfast idea",
    "What is machine learning?",
    "Write a short poem",
    "Who is the president of USA?",
    "How does WiFi work?"
]

for msg in small_talk:
    send(msg)
    time.sleep(1.5)

# ---- MEMORY TEST ----
print("\n=====================================")
print(" MEMORY RECALL TEST")
print("=====================================")

time.sleep(2)

send("Can you call me tomorrow?")

print("\n=====================================")
print(" DEMO COMPLETE")
print("=====================================")
