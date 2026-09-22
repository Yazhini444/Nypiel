"""
Lightweight keyword-retrieval chatbot: no external API key required, so the
app works offline out of the box. It answers from a small skincare knowledge
base and, when a scan_id is supplied, grounds its answer in that user's own
skin type / concerns / recommendations.

To upgrade quality later, swap `answer()`'s body for a call to an LLM
(Anthropic API, etc.), keeping the KB text as the system prompt / context —
the function signature won't need to change.
"""
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

KB = {
    "dry": "Dry skin produces less natural oil and can feel tight, flaky, or "
           "rough. Look for hyaluronic acid and ceramides, and avoid harsh "
           "foaming cleansers.",
    "oily": "Oily skin overproduces sebum, often with visible shine and "
            "larger pores. Niacinamide and salicylic acid help regulate oil "
            "without over-stripping the skin.",
    "combination": "Combination skin is oily through the T-zone (forehead, "
                   "nose, chin) and normal-to-dry on the cheeks. It usually "
                   "needs different products in different zones.",
    "normal": "Normal skin is well-balanced — not too oily or too dry — and "
              "mainly needs maintenance: daily SPF, antioxidants, and "
              "consistent hydration.",
    "acne": "Acne is caused by clogged pores, excess oil, and bacteria. "
            "Salicylic acid is the go-to exfoliant; avoid over-washing, "
            "which can trigger more oil production.",
    "dark_spots": "Dark spots (hyperpigmentation) form from sun exposure, "
                  "old acne marks, or hormonal changes. Vitamin C and "
                  "alpha arbutin fade them gradually; daily SPF prevents "
                  "new ones.",
    "wrinkles": "Fine lines and wrinkles come from collagen loss over time. "
                "Retinol is the most-studied ingredient for this — start "
                "2-3x/week to build tolerance.",
    "redness": "Redness usually signals a compromised skin barrier or "
               "sensitivity. Azelaic acid and centella asiatica calm "
               "irritation; introduce new actives one at a time.",
    "retinol": "Retinol speeds up cell turnover and boosts collagen. Use it "
               "at night only, start 1-3x/week, and always follow with SPF "
               "the next morning — it increases sun sensitivity.",
    "niacinamide": "Niacinamide balances oil, minimizes the look of pores, "
                   "and strengthens the skin barrier. It's gentle enough "
                   "for daily AM and PM use and layers well with almost "
                   "everything.",
    "salicylic acid": "Salicylic acid is an oil-soluble exfoliant that gets "
                       "inside pores to clear congestion — best for oily "
                       "or acne-prone skin, used 2-3x/week at night.",
    "vitamin c": "Vitamin C is an antioxidant that brightens skin and fades "
                 "dark spots. Use it in the morning under sunscreen for the "
                 "best protective effect.",
    "spf": "Sunscreen is the single most important daily step — it prevents "
           "new dark spots, redness, and premature wrinkles regardless of "
           "skin type.",
    "routine": "A simple routine works best: cleanse, treat (your active "
               "ingredient), moisturize, and SPF in the morning. Introduce "
               "one new active at a time so you can tell what's working.",
}

FALLBACK = ("I can help with skin types, concerns, and ingredients like "
            "retinol, niacinamide, vitamin C, and salicylic acid — try "
            "asking about one of those, or about your last scan result.")


def _scan_context(db: Any, scan_id: Optional[int], user_id: int) -> str:
    if scan_id is None:
        return ""
    from . import models
    scan = (
        db.query(models.ScanResult)
        .filter(models.ScanResult.id == scan_id, models.ScanResult.owner_id == user_id)
        .first()
    )
    if not scan:
        return ""
    concern_labels = ", ".join(c["label"].replace("_", " ") for c in scan.concerns)
    top_recs = ", ".join(r["ingredient"] for r in scan.recommendations[:3])
    return (f"Your last scan found {scan.skin_type} skin with these concerns: "
            f"{concern_labels}. Suggested ingredients: {top_recs}. ")


def answer(question: str, db: Any, user_id: int, scan_id: Optional[int] = None) -> str:
    q = question.lower()
    context = _scan_context(db, scan_id, user_id)

    hits = [text for key, text in KB.items() if key in q]
    if hits:
        return (context + " ".join(hits)).strip()

    if context and any(w in q for w in ["my skin", "my result", "my scan", "what should i use", "recommend"]):
        return context.strip()

    return (context + FALLBACK).strip()
