"""Small fixture module used by the Codex Evidence RAG test suite."""


def retrieve_context(question: str, documents: list[str]) -> list[str]:
    terms = {term.lower() for term in question.split() if len(term) > 2}
    return [doc for doc in documents if terms & {word.lower().strip(".,") for word in doc.split()}]


def grade_claim(matches: int) -> str:
    if matches >= 3:
        return "STRONG"
    if matches >= 2:
        return "MEDIUM"
    if matches >= 1:
        return "WEAK"
    return "UNVERIFIED"
