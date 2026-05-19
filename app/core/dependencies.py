from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

_paddle_ocr: Any = None
_nlp: Any = None
_embedder: Any = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_paddle_ocr() -> Any:
    if _paddle_ocr is None:
        raise RuntimeError("PaddleOCR is not loaded")
    return _paddle_ocr


def get_nlp() -> Any:
    if _nlp is None:
        raise RuntimeError("spaCy model is not loaded")
    return _nlp


def get_embedder() -> Any:
    if _embedder is None:
        raise RuntimeError("Sentence transformer is not loaded")
    return _embedder


def load_paddle_ocr() -> None:
    global _paddle_ocr
    from paddleocr import PaddleOCR
    _paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)


def load_nlp() -> None:
    global _nlp
    import spacy
    _nlp = spacy.load("en_core_web_sm")


def load_embedder() -> None:
    global _embedder
    from sentence_transformers import SentenceTransformer
    from app.core.config import settings
    _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
