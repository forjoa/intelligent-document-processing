import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

import io
import sys
from unittest.mock import MagicMock, patch
import pytest

# Stub heavy imports before the module loads
_pytesseract_stub = MagicMock()
_PIL_stub = MagicMock()
sys.modules.setdefault("pytesseract", _pytesseract_stub)
sys.modules.setdefault("PIL", _PIL_stub)
sys.modules.setdefault("PIL.Image", _PIL_stub)

from app.services.ocr import run_ocr, OCRResult
from app.core.exceptions import OCRFailure


def _make_paddle(text: str, confidence: float) -> MagicMock:
    """PaddleOCR mock returning a single line with given text and confidence."""
    paddle = MagicMock()
    paddle.ocr.return_value = [[[None, (text, confidence)]]]
    return paddle


def _fake_image_bytes() -> bytes:
    """Minimal PNG bytes so PIL.Image.open succeeds (mocked anyway)."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _patch_tesseract(words: list[str], confs: list[int]) -> None:
    """Configure the tesseract stub to return given words and confidences."""
    import pytesseract
    pytesseract.Output = MagicMock()
    pytesseract.Output.DICT = "dict"
    pytesseract.image_to_data.return_value = {"conf": confs, "text": words}
    import PIL.Image
    PIL.Image.open.return_value = MagicMock()


def test_run_ocr_paddle_above_threshold_uses_paddle() -> None:
    paddle = _make_paddle("Hello World", 0.95)
    _patch_tesseract([], [])
    result = run_ocr([_fake_image_bytes()], paddle, confidence_threshold=0.8)
    assert result.engine_used == "paddleocr"
    assert result.text == "Hello World"
    assert result.confidence == pytest.approx(0.95)


def test_run_ocr_paddle_below_threshold_falls_back_to_tesseract() -> None:
    paddle = _make_paddle("blurry", 0.3)
    _patch_tesseract(["Clear", "Text"], [85, 90])
    result = run_ocr([_fake_image_bytes()], paddle, confidence_threshold=0.8)
    assert result.engine_used == "tesseract"


def test_run_ocr_tesseract_confidence_higher_than_paddle() -> None:
    paddle = _make_paddle("low quality", 0.5)
    _patch_tesseract(["Good", "Text"], [92, 88])
    result = run_ocr([_fake_image_bytes()], paddle, confidence_threshold=0.9)
    assert result.engine_used == "tesseract"
    assert result.confidence > 0.5


def test_run_ocr_both_zero_confidence_raises_ocr_failure() -> None:
    paddle = MagicMock()
    paddle.ocr.return_value = [[]]  # empty result -> confidence 0.0
    _patch_tesseract([], [])  # no words -> confidence 0.0
    with pytest.raises(OCRFailure):
        run_ocr([_fake_image_bytes()], paddle, confidence_threshold=0.8)


def test_run_ocr_returns_ocr_result_type() -> None:
    paddle = _make_paddle("text", 0.9)
    result = run_ocr([_fake_image_bytes()], paddle, confidence_threshold=0.8)
    assert isinstance(result, OCRResult)
