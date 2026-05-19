import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

import numpy as np
import pytest
from unittest.mock import MagicMock

from app.services.embedder import embed
from app.core.exceptions import EmbeddingError


def _make_model(vector: np.ndarray) -> MagicMock:
    model = MagicMock()
    model.encode.return_value = vector
    return model


def test_embed_returns_list_of_floats() -> None:
    vec = np.ones(384, dtype=np.float32)
    model = _make_model(vec)
    result = embed("some text", model)
    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(v, float) for v in result)


def test_embed_calls_encode_with_normalize() -> None:
    vec = np.zeros(384, dtype=np.float32)
    model = _make_model(vec)
    embed("hello", model)
    model.encode.assert_called_once_with("hello", normalize_embeddings=True)


def test_embed_values_match_vector() -> None:
    values = list(range(384))
    vec = np.array(values, dtype=np.float32)
    model = _make_model(vec)
    result = embed("text", model)
    assert result[0] == pytest.approx(0.0)
    assert result[1] == pytest.approx(1.0)


def test_embed_raises_embedding_error_on_exception() -> None:
    model = MagicMock()
    model.encode.side_effect = RuntimeError("GPU out of memory")
    with pytest.raises(EmbeddingError):
        embed("text", model)


def test_embed_error_message_contains_original_cause() -> None:
    model = MagicMock()
    model.encode.side_effect = ValueError("bad input shape")
    with pytest.raises(EmbeddingError, match="bad input shape"):
        embed("text", model)
