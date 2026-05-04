def is_viable_candidate(normalized_doc: dict[str, str]) -> bool:
    text = normalized_doc.get("raw_text", "")
    if len(text) < 100:
        return False
    return True
