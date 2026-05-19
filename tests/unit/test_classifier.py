import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

from app.services.classifier import classify, ClassificationResult


def test_classify_invoice_keywords() -> None:
    result = classify("Invoice #1234 Amount Due: $500 VAT vendor payment", 0.4)
    assert result.document_type == "invoice"
    assert result.confidence > 0.5


def test_classify_ticket_keywords() -> None:
    result = classify("Boarding pass ticket gate A12 seat 14B event venue", 0.4)
    assert result.document_type == "ticket"


def test_classify_cv_keywords() -> None:
    result = classify("Curriculum vitae skills experience education references objective", 0.4)
    assert result.document_type == "cv"


def test_classify_empty_text_returns_unknown() -> None:
    result = classify("", 0.4)
    assert result.document_type == "unknown"


def test_classify_gibberish_returns_unknown() -> None:
    result = classify("zzz qqq bbb xxx yyy", 0.4)
    assert result.document_type == "unknown"


def test_classify_low_confidence_returns_unknown() -> None:
    # Mixed keywords spread scores across types: ticket wins with ~0.42 confidence
    # Setting min_confidence=0.5 forces the result to "unknown"
    result = classify("total ticket skills event education bill", 0.5)
    assert result.document_type == "unknown"
    assert result.confidence < 0.5


def test_classify_all_zero_scores_confidence_is_1() -> None:
    result = classify("", 0.4)
    assert result.document_type == "unknown"
    assert result.confidence == 1.0


def test_classify_returns_classification_result_type() -> None:
    result = classify("invoice bill payment", 0.4)
    assert isinstance(result, ClassificationResult)


def test_classify_confidence_between_0_and_1() -> None:
    result = classify("invoice bill amount due vendor vat", 0.4)
    assert 0.0 <= result.confidence <= 1.0
