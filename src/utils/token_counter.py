def count_tokens(text: str) -> int:
    """Count tokens in text. Simple whitespace-based for now."""
    return len(text.split())
