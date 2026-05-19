import io
from dataclasses import dataclass
from typing import Any

import pytesseract
from PIL import Image

from app.core.exceptions import OCRFailure


@dataclass
class OCRResult:
    text: str
    confidence: float
    engine_used: str  # "paddleocr" | "tesseract"


def _run_paddle(images: list[bytes], paddle_ocr: Any) -> tuple[str, float]:
    all_text: list[str] = []
    all_confidences: list[float] = []

    for img_bytes in images:
        result = paddle_ocr.ocr(img_bytes, cls=True)
        if not result or not result[0]:
            continue
        for line in result[0]:
            text_content, confidence = line[1]
            all_text.append(text_content)
            all_confidences.append(float(confidence))

    if not all_confidences:
        return "", 0.0

    return " ".join(all_text), sum(all_confidences) / len(all_confidences)


def _run_tesseract(images: list[bytes]) -> tuple[str, float]:
    all_text: list[str] = []

    for img_bytes in images:
        image = Image.open(io.BytesIO(img_bytes))
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [c for c in data["conf"] if isinstance(c, (int, float)) and c >= 0]
        words = [
            data["text"][i]
            for i, c in enumerate(data["conf"])
            if isinstance(c, (int, float)) and c >= 0 and data["text"][i].strip()
        ]
        all_text.extend(words)

    text = " ".join(all_text)
    # Tesseract confidence is 0-100; normalize to 0.0-1.0
    if not all_text:
        return "", 0.0

    page_texts = []
    page_confidences: list[float] = []
    for img_bytes in images:
        image = Image.open(io.BytesIO(img_bytes))
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confs = [c / 100.0 for c in data["conf"] if isinstance(c, (int, float)) and c >= 0]
        page_confidences.extend(confs)

    avg_conf = sum(page_confidences) / len(page_confidences) if page_confidences else 0.0
    return text, avg_conf


def run_ocr(images: list[bytes], paddle_ocr: Any, confidence_threshold: float) -> OCRResult:
    paddle_text, paddle_conf = _run_paddle(images, paddle_ocr)

    if paddle_conf >= confidence_threshold:
        return OCRResult(text=paddle_text, confidence=paddle_conf, engine_used="paddleocr")

    tesseract_text, tesseract_conf = _run_tesseract(images)

    if tesseract_conf == 0.0 and paddle_conf == 0.0:
        raise OCRFailure("Both PaddleOCR and Tesseract returned zero confidence")

    if tesseract_conf >= paddle_conf:
        return OCRResult(text=tesseract_text, confidence=tesseract_conf, engine_used="tesseract")

    return OCRResult(text=paddle_text, confidence=paddle_conf, engine_used="paddleocr")
