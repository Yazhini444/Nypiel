"""
Rule-based ingredient recommendation engine. Deterministic and editable by
a non-ML person on the team — swap for a learned ranker later if you want,
the output shape (list of Recommendation dicts) is what the frontend expects.
"""
from typing import List, Dict, Any

# skin type -> baseline ingredients everyone with that type benefits from
SKIN_TYPE_BASE: Dict[str, List[Dict[str, str]]] = {
    "dry": [
        {"ingredient": "Hyaluronic Acid", "why": "Draws in and holds moisture in dry skin.",
         "use": "AM & PM", "frequency": "Daily"},
        {"ingredient": "Ceramides", "why": "Rebuilds the moisture barrier dry skin tends to lose.",
         "use": "PM", "frequency": "Daily"},
    ],
    "oily": [
        {"ingredient": "Niacinamide", "why": "Regulates oil production and visibly tightens pores.",
         "use": "AM & PM", "frequency": "Daily"},
        {"ingredient": "Salicylic Acid", "why": "Cuts through excess oil and clears clogged pores.",
         "use": "PM", "frequency": "2-3x / week"},
    ],
    "combination": [
        {"ingredient": "Niacinamide", "why": "Balances oil in the T-zone without over-drying the cheeks.",
         "use": "AM & PM", "frequency": "Daily"},
        {"ingredient": "Hyaluronic Acid", "why": "Hydrates drier areas without adding oil.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "normal": [
        {"ingredient": "Vitamin C", "why": "Protects and brightens as a daily maintenance step.",
         "use": "AM", "frequency": "Daily"},
        {"ingredient": "Hyaluronic Acid", "why": "Keeps hydration levels topped up.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
}

# concern -> targeted ingredient(s)
CONCERN_INGREDIENTS: Dict[str, List[Dict[str, str]]] = {
    "acne": [{"ingredient": "Salicylic Acid", "why": "Exfoliates inside the pore to clear breakouts.",
               "use": "PM", "frequency": "2-3x / week"}],
    "dark_spots": [{"ingredient": "Vitamin C", "why": "Fades discoloration and evens tone over time.",
                     "use": "AM", "frequency": "Daily"},
                    {"ingredient": "Alpha Arbutin", "why": "Targets stubborn dark spots directly.",
                     "use": "PM", "frequency": "Daily"}],
    "wrinkles": [{"ingredient": "Retinol", "why": "Speeds up cell turnover to soften fine lines.",
                  "use": "PM", "frequency": "2-3x / week"},
                 {"ingredient": "Peptides", "why": "Supports collagen for firmer-looking skin.",
                  "use": "AM & PM", "frequency": "Daily"}],
    "redness": [{"ingredient": "Azelaic Acid", "why": "Calms redness and evens out skin tone.",
                 "use": "AM or PM", "frequency": "Daily"},
                {"ingredient": "Centella Asiatica", "why": "Soothes and repairs an irritated barrier.",
                 "use": "AM & PM", "frequency": "Daily"}],
    "large_pores": [{"ingredient": "Niacinamide", "why": "Refines the look of enlarged pores.",
                      "use": "AM & PM", "frequency": "Daily"}],
    "dark_circles": [{"ingredient": "Caffeine", "why": "De-puffs and brightens the under-eye area.",
                       "use": "AM", "frequency": "Daily"},
                      {"ingredient": "Peptides", "why": "Firms thin under-eye skin over time.",
                       "use": "PM", "frequency": "Daily"}],
    "blackheads": [{"ingredient": "Salicylic Acid", "why": "Dissolves the buildup that forms blackheads.",
                     "use": "PM", "frequency": "2-3x / week"}],
    "uneven_texture": [{"ingredient": "Glycolic Acid", "why": "Exfoliates the surface for smoother texture.",
                         "use": "PM", "frequency": "1-3x / week"}],
    "dehydration": [{"ingredient": "Hyaluronic Acid", "why": "Replenishes water content at the surface.",
                      "use": "AM & PM", "frequency": "Daily"}],
    "dullness": [{"ingredient": "Vitamin C", "why": "Brightens and restores radiance.",
                  "use": "AM", "frequency": "Daily"}],
}


def build_recommendations(skin_type: str, concerns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []

    for rec in SKIN_TYPE_BASE.get(skin_type, []):
        if rec["ingredient"] not in seen:
            out.append(rec)
            seen.add(rec["ingredient"])

    # sort concerns by confidence so the most confident findings drive the top recs
    for concern in sorted(concerns, key=lambda c: c.get("confidence", 0), reverse=True):
        for rec in CONCERN_INGREDIENTS.get(concern["label"], []):
            if rec["ingredient"] not in seen:
                out.append(rec)
                seen.add(rec["ingredient"])

    return out
