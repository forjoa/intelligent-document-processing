import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

from unittest.mock import MagicMock
from app.services.extractor import extract_fields


def _make_nlp(ents: list[tuple[str, str]]) -> MagicMock:
    """Return a minimal spaCy-like nlp mock producing the given (text, label_) entities."""
    nlp = MagicMock()
    doc = MagicMock()
    entity_mocks = []
    for text, label in ents:
        ent = MagicMock()
        ent.text = text
        ent.label_ = label
        entity_mocks.append(ent)
    doc.ents = entity_mocks
    nlp.return_value = doc
    return nlp


def test_extract_fields_unknown_returns_empty() -> None:
    nlp = _make_nlp([])
    result = extract_fields("any text", "unknown", nlp)
    assert result == {}


def test_extract_invoice_keys_present() -> None:
    text = "Invoice #INV-001\nAcme Corp\nDate: 2024-01-15\nTotal: $1,200.00 USD"
    nlp = _make_nlp([("Acme Corp", "ORG"), ("2024-01-15", "DATE")])
    result = extract_fields(text, "invoice", nlp)
    assert set(result.keys()) == {"company", "date", "total", "currency", "invoice_number"}


def test_extract_invoice_company_and_date() -> None:
    text = "Invoice #INV-042\nGlobal Ltd\nDate: March 2024\nAmount due $500 USD"
    nlp = _make_nlp([("Global Ltd", "ORG"), ("March 2024", "DATE")])
    result = extract_fields(text, "invoice", nlp)
    assert result["company"] == "Global Ltd"
    assert result["date"] == "March 2024"


def test_extract_invoice_number_parsed() -> None:
    text = "Invoice No. INV-9999\nTotal: $200 USD"
    nlp = _make_nlp([])
    result = extract_fields(text, "invoice", nlp)
    assert result["invoice_number"] == "INV-9999"


def test_extract_invoice_currency_detected() -> None:
    text = "Total: €450.00"
    nlp = _make_nlp([])
    result = extract_fields(text, "invoice", nlp)
    assert result["currency"] == "€"


def test_extract_invoice_missing_fields_are_none() -> None:
    text = "nothing useful here"
    nlp = _make_nlp([])
    result = extract_fields(text, "invoice", nlp)
    assert "company" in result
    assert result["company"] is None
    assert result["total"] is None


def test_extract_cv_keys_present() -> None:
    text = "Jane Doe\njane@example.com\n+1 555 123 4567\nSkills: Python, SQL\n\nSoftware Engineer\nTech Inc\n2020 - 2024"
    nlp = _make_nlp([("Jane Doe", "PERSON")])
    result = extract_fields(text, "cv", nlp)
    assert set(result.keys()) == {"name", "email", "phone", "skills", "experience"}


def test_extract_cv_name_from_nlp() -> None:
    text = "John Smith\njohn@example.com\nSkills: Java"
    nlp = _make_nlp([("John Smith", "PERSON")])
    result = extract_fields(text, "cv", nlp)
    assert result["name"] == "John Smith"


def test_extract_cv_email_extracted() -> None:
    text = "contact: user@domain.org\nSkills: Python"
    nlp = _make_nlp([])
    result = extract_fields(text, "cv", nlp)
    assert result["email"] == "user@domain.org"


def test_extract_cv_missing_fields_are_none_or_empty() -> None:
    text = "nothing useful"
    nlp = _make_nlp([])
    result = extract_fields(text, "cv", nlp)
    assert result["name"] is None
    assert result["email"] is None
    assert result["skills"] == []
    assert result["experience"] == []
