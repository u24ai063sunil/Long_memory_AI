import math

def score_memory(memory, current_turn):

    confidence = memory["meta"]["confidence"]
    last_used = memory["meta"]["last_used_turn"]

    recency = math.exp(-(current_turn-last_used)/50)

    return 0.7*confidence + 0.3*recency


# def rank_memories(memories, current_turn):
#     return sorted(memories, key=lambda m: score_memory(m,current_turn), reverse=True)[:3]
# def rank_memories(memories, current_turn):

#     if not memories:
#         return []

#     ranked = []

#     for m in memories:
#         score = 0

#         text = m.get("text", "").lower()
#         meta = m.get("meta", {})

#         # 1️⃣ relevance scoring (most important)
#         if any(word in text for word in ["time", "call", "schedule", "contact"]):
#             score += 5

#         if any(word in text for word in ["vegetarian", "diet", "eat", "food"]):
#             score += 3

#         if any(word in text for word in ["project", "study", "work", "hackathon"]):
#             score += 4

#         # 2️⃣ recency scoring
#         last_used = meta.get("last_used_turn", 0)
#         score += max(0, 5 - (current_turn - last_used))

#         # 3️⃣ confidence scoring
#         score += meta.get("confidence", 0)

#         ranked.append((score, m))

#     ranked.sort(key=lambda x: x[0], reverse=True)

#     # Only send top 2 memories to LLM
#     return [m for _, m in ranked[:2]]
def rank_memories(memories, current_turn):

    if not memories:
        return []

    ranked = []

    for m in memories:
        score = 0

        text = m.get("text", "").lower()
        meta = m.get("meta", {})

        # -------- relevance scoring (MOST IMPORTANT) --------
        if any(word in text for word in ["time", "call", "schedule", "contact", "after"]):
            score += 10

        if any(word in text for word in ["vegetarian", "diet", "eat", "food"]):
            score += 8

        if any(word in text for word in ["project", "hackathon", "study", "work"]):
            score += 9

        # -------- confidence --------
        score += meta.get("confidence", 0)

        ranked.append((score, m))

    ranked.sort(key=lambda x: x[0], reverse=True)

    # Only send top 2 memories to the LLM
    return [m for _, m in ranked[:3]]

