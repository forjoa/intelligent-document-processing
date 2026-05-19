from typing import Any

from app.core.exceptions import EmbeddingError


def embed(text: str, model: Any) -> list[float]:
    try:
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    except Exception as exc:
        raise EmbeddingError(f"Model inference failed: {exc}") from exc
