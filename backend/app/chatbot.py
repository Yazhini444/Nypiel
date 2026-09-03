"""
AI Skincare Chatbot powered by Google Gemini (gemini-3.5-flash) with
intelligent scan-result grounding and offline rule-based fallback.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_gemini_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("[nypiel] Gemini AI client initialized for Chatbot.")
    except Exception as exc:
        print(f"[nypiel] Could not initialize Gemini client: {exc}")
        _gemini_client = None

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


def _scan_context(db: Session, scan_id: Optional[int], user_id: int) -> str:
    if scan_id is None:
        return ""
    scan = (
        db.query(models.ScanResult)
        .filter(models.ScanResult.id == scan_id, models.ScanResult.owner_id == user_id)
        .first()
    )
    if not scan:
        return ""
    concern_labels = ", ".join(c["label"].replace("_", " ").title() for c in scan.concerns)
    recs_detail = ", ".join(f"{r['ingredient']} ({r.get('use', 'daily')})" for r in scan.recommendations)
    return (f"User's Latest Skin Scan Analysis:\n"
            f"- Skin Type: {scan.skin_type.capitalize()} (Confidence: {int(scan.skin_type_confidence * 100)}%)\n"
            f"- Detected Concerns: {concern_labels if concern_labels else 'None detected'}\n"
            f"- Personalized Recommended Ingredients: {recs_detail}\n")


def _answer_with_gemini(question: str, context: str) -> Optional[str]:
    """Generates an answer using Google Gemini 3.5 Flash."""
    global _gemini_client
    if _gemini_client is None:
        return None

    system_instruction = (
        "You are 'nypiel AI', an expert, elegant, and highly helpful skincare consultant for the brand nypiel. "
        "Your mission is to provide personalized, science-backed, and practical skincare guidance. "
        "Guidelines:\n"
        "1. When user scan data is provided, reference their specific skin type and concerns directly.\n"
        "2. Suggest step-by-step layering routines (AM vs. PM) and proper frequencies (e.g. daily, 2-3x weekly).\n"
        "3. Warn about ingredient clashes (e.g. do not mix Retinol and strong exfoliating acids in the same PM routine).\n"
        "4. Emphasize sunscreen (SPF) with active ingredients like Vitamin C and Retinol.\n"
        "5. Keep answers concise, clear, and easy to follow. Use bullet points where appropriate.\n"
        "6. Maintain a supportive, reassuring, and premium tone."
    )

    prompt = f"System Context:\n{system_instruction}\n\n"
    if context:
        prompt += f"{context}\n\n"
    prompt += f"User Question: {question}\n\nYour Answer:"

    models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]
    for m in models_to_try:
        try:
            response = _gemini_client.models.generate_content(
                model=m,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception as exc:
            print(f"[nypiel] Gemini call to '{m}' failed: {exc}")

    return None


def answer(question: str, db: Session, user_id: int, scan_id: Optional[int] = None) -> str:
    context = _scan_context(db, scan_id, user_id)

    # 1. Attempt generation with Gemini Flash
    gemini_reply = _answer_with_gemini(question, context)
    if gemini_reply:
        return gemini_reply

    # 2. Offline fallback (keyword retrieval)
    q = question.lower()
    hits = [text for key, text in KB.items() if key in q]
    if hits:
        prefix = f"Based on your scan ({context.strip()}): " if context else ""
        return (prefix + " ".join(hits)).strip()

    if context and any(w in q for w in ["my skin", "my result", "my scan", "what should i use", "recommend"]):
        return context.strip()

    prefix = f"Based on your scan ({context.strip()}): " if context else ""
    return (prefix + FALLBACK).strip()

