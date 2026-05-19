from dataclasses import dataclass

DOCUMENT_TYPES: tuple[str, ...] = ("invoice", "ticket", "contract", "cv", "unknown")

KEYWORD_TABLE: dict[str, list[tuple[str, int]]] = {
    "invoice": [
        ("invoice", 3), ("bill", 2), ("amount due", 3), ("vat", 2),
        ("total", 1), ("payment", 1), ("vendor", 2), ("invoice number", 3),
    ],
    "ticket": [
        ("ticket", 3), ("seat", 2), ("gate", 2), ("boarding", 3),
        ("row", 1), ("event", 2), ("venue", 2), ("price", 1),
    ],
    "contract": [
        ("agreement", 3), ("contract", 3), ("parties", 2), ("whereas", 3),
        ("governing law", 3), ("jurisdiction", 2), ("clause", 2),
    ],
    "cv": [
        ("curriculum vitae", 3), ("resume", 3), ("experience", 2),
        ("education", 2), ("skills", 2), ("references", 1), ("objective", 1),
    ],
}

_MAX_PHRASE_OCCURRENCES = 3


@dataclass
class ClassificationResult:
    document_type: str
    confidence: float


def _score_type(text: str, phrases: list[tuple[str, int]]) -> int:
    score = 0
    for phrase, weight in phrases:
        occurrences = min(text.count(phrase), _MAX_PHRASE_OCCURRENCES)
        score += occurrences * weight
    return score


def classify(text: str, min_confidence: float) -> ClassificationResult:
    lowered = text.lower()
    scores = {doc_type: _score_type(lowered, phrases) for doc_type, phrases in KEYWORD_TABLE.items()}

    total = sum(scores.values())
    if total == 0:
        return ClassificationResult(document_type="unknown", confidence=1.0)

    winner = max(scores, key=lambda k: scores[k])
    confidence = scores[winner] / total

    if confidence < min_confidence:
        return ClassificationResult(document_type="unknown", confidence=confidence)

    return ClassificationResult(document_type=winner, confidence=confidence)
