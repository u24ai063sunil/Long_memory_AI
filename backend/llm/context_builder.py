def build_context(memories):

    # no memories retrieved
    if not memories or not isinstance(memories, list):
        return ""

    context_lines = []

    for m in memories:
        try:
            # safe extraction
            meta = m.get("meta", {})
            value = m.get("text", "")

            if not value:
                continue

            key = meta.get("key", "")

            # special handling for call preference
            if key == "call_time":
                context_lines.append(
                    f"The user prefers to be contacted {value}."
                )
            else:
                context_lines.append(value)

        except Exception as e:
            print("Context parse error:", e)
            continue

    # if nothing usable
    if not context_lines:
        return ""

    context = "IMPORTANT USER FACTS:\n"
    for line in context_lines:
        context += f"- {line}\n"

    context += "\nUse these facts when relevant while answering."

    return context
