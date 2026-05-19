import re
from typing import Any

from app.core.exceptions import ExtractionError

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"[\+]?[\d\s\-().]{7,20}")
_INVOICE_NUM_RE = re.compile(r"(?:invoice\s*[#nNo.:]+\s*)([A-Z0-9\-]+)", re.IGNORECASE)
_CURRENCY_RE = re.compile(r"(USD|EUR|GBP|CAD|AUD|\$|€|£)")
_PRICE_RE = re.compile(r"[\$€£]?\s*\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?")
_TOTAL_RE = re.compile(r"(?:total|amount due|balance due)[^\d]*([\$€£]?\s*[\d,. ]+)", re.IGNORECASE)


def extract_fields(text: str, document_type: str, nlp: Any) -> dict[str, Any]:
    try:
        if document_type == "invoice":
            return _extract_invoice(text, nlp)
        if document_type == "ticket":
            return _extract_ticket(text, nlp)
        if document_type == "contract":
            return _extract_contract(text, nlp)
        if document_type == "cv":
            return _extract_cv(text, nlp)
        return {}
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"spaCy pipeline failed: {exc}") from exc


def _extract_invoice(text: str, nlp: Any) -> dict[str, Any]:
    doc = nlp(text)
    company: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ == "ORG"), None
    )
    date: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ == "DATE"), None
    )
    total_match = _TOTAL_RE.search(text)
    total: str | None = total_match.group(1).strip() if total_match else None

    currency_match = _CURRENCY_RE.search(text)
    currency: str | None = currency_match.group(1) if currency_match else None

    inv_match = _INVOICE_NUM_RE.search(text)
    invoice_number: str | None = inv_match.group(1) if inv_match else None

    return {
        "company": company,
        "date": date,
        "total": total,
        "currency": currency,
        "invoice_number": invoice_number,
    }


def _extract_ticket(text: str, nlp: Any) -> dict[str, Any]:
    doc = nlp(text)
    event_or_route: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ in ("EVENT", "FAC", "LOC", "ORG")), None
    )
    date: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ == "DATE"), None
    )
    seat_match = re.search(r"(?:seat|row|section)[^\w]*([A-Z0-9]+)", text, re.IGNORECASE)
    seat_or_section: str | None = seat_match.group(1) if seat_match else None

    price_match = _PRICE_RE.search(text)
    price: str | None = price_match.group(0).strip() if price_match else None

    return {
        "event_or_route": event_or_route,
        "date": date,
        "seat_or_section": seat_or_section,
        "price": price,
    }


def _extract_contract(text: str, nlp: Any) -> dict[str, Any]:
    doc = nlp(text)
    parties: list[str] = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "PERSON")]

    date: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ == "DATE"), None
    )
    gov_law_match = re.search(
        r"governing\s+law[^a-zA-Z]*([A-Z][a-zA-Z\s]+?)(?:\.|,|\n)", text, re.IGNORECASE
    )
    governing_law: str | None = gov_law_match.group(1).strip() if gov_law_match else None

    return {
        "parties": list(dict.fromkeys(parties)),
        "effective_date": date,
        "governing_law": governing_law,
    }


def _extract_cv(text: str, nlp: Any) -> dict[str, Any]:
    doc = nlp(text)
    name: str | None = next(
        (ent.text for ent in doc.ents if ent.label_ == "PERSON"), None
    )
    email_match = _EMAIL_RE.search(text)
    email: str | None = email_match.group(0) if email_match else None

    phone_match = _PHONE_RE.search(text)
    phone: str | None = phone_match.group(0).strip() if phone_match else None

    skills_match = re.search(
        r"skills[:\s]+(.*?)(?:\n\n|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    skills: list[str] = []
    if skills_match:
        raw = skills_match.group(1)
        skills = [s.strip() for s in re.split(r"[,\n•\-|]", raw) if s.strip()]

    experience_blocks = re.findall(
        r"(?P<title>[A-Z][^\n]+)\n(?P<org>[A-Z][^\n]+)\n(?P<period>\d{4}[^\n]+)",
        text,
    )
    experience: list[dict[str, str]] = [
        {"title": t.strip(), "organization": o.strip(), "period": p.strip()}
        for t, o, p in experience_blocks
    ]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "experience": experience,
    }
