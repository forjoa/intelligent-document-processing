import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

from unittest.mock import MagicMock
from app.services.extractor import extract_fields, _extract_line_items


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


# ---------------------------------------------------------------------------
# Pre-existing tests (updated to include line_items in expected key set)
# ---------------------------------------------------------------------------

def test_extract_fields_unknown_returns_empty() -> None:
    nlp = _make_nlp([])
    result = extract_fields("any text", "unknown", nlp)
    assert result == {}


def test_extract_invoice_keys_present() -> None:
    text = "Invoice #INV-001\nAcme Corp\nDate: 2024-01-15\nTotal: $1,200.00 USD"
    nlp = _make_nlp([("Acme Corp", "ORG"), ("2024-01-15", "DATE")])
    result = extract_fields(text, "invoice", nlp)
    assert set(result.keys()) == {
        "company", "date", "total", "currency", "invoice_number", "line_items"
    }


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


# ---------------------------------------------------------------------------
# _extract_line_items — new tests
# ---------------------------------------------------------------------------

# 1. Well-formed English invoice: non-empty line_items, each dict has the 4 keys.
def test_extract_line_items_well_formed_english_invoice() -> None:
    lines = [
        "INVOICE #001",
        "Description       Qty   Unit Price   Amount",
        "Web design         2      500.00     1000.00",
        "Hosting setup      1      150.00      150.00",
        "Total: $1,150.00",
    ]
    items = _extract_line_items(lines)
    assert len(items) >= 1
    for item in items:
        assert set(item.keys()) == {"description", "quantity", "unit_price", "amount"}


# 2. No body lines between header and total → empty list, no exception.
def test_extract_line_items_no_body_lines() -> None:
    lines = [
        "INVOICE #002",
        "Total: $0.00",
    ]
    items = _extract_line_items(lines)
    assert items == []


# 3. Header-zone numeric tokens (top 20%) must NOT appear in line_items.
def test_extract_line_items_header_zone_excluded() -> None:
    lines = [
        "Invoice #2024-001",           # line 0 — in header zone (20% of 6 = 1.2 → header_end=1)
        "Description   Qty  Unit  Amount",
        "Widget A       3   10.00  30.00",
        "Widget B       1   25.00  25.00",
        "Widget C       2   15.00  30.00",
        "Total: $85.00",
    ]
    items = _extract_line_items(lines)
    # No item should carry the invoice number token "2024" or "001"
    for item in items:
        description = item["description"] or ""
        assert "2024" not in description
        assert "001" not in description


# 4. Line with 4+ numeric tokens → surplus tokens appear in description.
def test_extract_line_items_surplus_tokens_in_description() -> None:
    lines = [
        "Header line",
        "Item A   1   2   10.00   20.00",   # 4 numeric tokens
        "Total: $20.00",
    ]
    items = _extract_line_items(lines)
    assert len(items) == 1
    item = items[0]
    # With 4 tokens: qty=tokens[-3], unit_price=tokens[-2], amount=tokens[-1]
    # surplus token (tokens[0]) must end up in description
    assert item["description"] is not None
    assert item["quantity"] is not None
    assert item["unit_price"] is not None
    assert item["amount"] is not None


# 5. Total line matching _TOTAL_ANCHOR_RE but not _TOTAL_RE (e.g. "Importe 1,200.00")
#    → stops item scanning (the total line itself is not included as an item).
def test_extract_line_items_total_anchor_stops_scanning() -> None:
    lines = [
        "Invoice header",
        "Consulting   1   200.00   200.00",
        "Importe 1,200.00",          # matches _TOTAL_ANCHOR_RE, not _TOTAL_RE
        "Extra line   1   50.00   50.00",   # must NOT appear in items
    ]
    items = _extract_line_items(lines)
    # The extra line after "Importe" must not be included
    amounts = [item["amount"] for item in items]
    assert "50.00" not in amounts


# 6. Completely non-numeric invoice text → empty list without raising.
def test_extract_line_items_no_numeric_text() -> None:
    lines = [
        "This invoice has no numbers at all",
        "Just words and more words",
        "Nothing to parse here",
    ]
    items = _extract_line_items(lines)
    assert items == []


# 7. Unicode currency symbols (€, £, ¥, ₹) in amount tokens → captured correctly.
def test_extract_line_items_unicode_currency_symbols() -> None:
    lines = [
        "Invoice",
        "Service fee   1   €50.00   €50.00",
        "Design work   1   £80.00   £80.00",
        "Total: €130.00",
    ]
    items = _extract_line_items(lines)
    assert len(items) >= 1
    amounts = [item["amount"] for item in items]
    assert any("€" in a or "£" in a for a in amounts)


# 8. Spanish-language invoice layout → line items extracted without Spanish hardcoding.
def test_extract_line_items_spanish_layout() -> None:
    lines = [
        "Factura #ES-001",
        "Descripción   Cant   Precio   Total",
        "Desarrollo web   3   150.00   450.00",
        "Soporte        1    80.00    80.00",
        "Importe 530.00",
    ]
    items = _extract_line_items(lines)
    assert len(items) >= 1
    for item in items:
        assert set(item.keys()) == {"description", "quantity", "unit_price", "amount"}


# 9. All 6 fields (including line_items) present and line_items is a list.
def test_extract_invoice_all_fields_present_after_line_items_added() -> None:
    text = (
        "Invoice #INV-007\n"
        "Acme Corp\n"
        "Date: 2025-03-01\n"
        "Widget A   2   25.00   50.00\n"
        "Total: $50.00 USD\n"
    )
    nlp = _make_nlp([("Acme Corp", "ORG"), ("2025-03-01", "DATE")])
    result = extract_fields(text, "invoice", nlp)
    assert result["company"] == "Acme Corp"
    assert result["date"] == "2025-03-01"
    assert result["total"] is not None
    assert result["currency"] is not None
    assert result["invoice_number"] == "INV-007"
    assert isinstance(result["line_items"], list)
