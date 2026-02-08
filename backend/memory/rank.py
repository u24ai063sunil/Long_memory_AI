import math

def score_memory(memory, current_turn):

    confidence = memory["meta"]["confidence"]
    last_used = memory["meta"]["last_used_turn"]

    recency = math.exp(-(current_turn-last_used)/50)

    return 0.7*confidence + 0.3*recency


def rank_memories(memories, current_turn):
    return sorted(memories, key=lambda m: score_memory(m,current_turn), reverse=True)[:3]
