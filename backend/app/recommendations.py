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
    "acne": [
        {"ingredient": "Salicylic Acid", "why": "Exfoliates inside the pore to clear breakouts.",
         "use": "PM", "frequency": "2-3x / week"},
    ],
    "blackheads": [
        {"ingredient": "Salicylic Acid (BHA)", "why": "Dissolves the sebum and dead skin buildup that forms blackheads.",
         "use": "PM", "frequency": "2-3x / week"},
    ],
    "whiteheads": [
        {"ingredient": "Salicylic Acid", "why": "Penetrates clogged pores to clear closed comedones.",
         "use": "PM", "frequency": "2-3x / week"},
        {"ingredient": "Azelaic Acid", "why": "Reduces cellular buildup and prevents pore blockage.",
         "use": "AM or PM", "frequency": "Daily"},
    ],
    "dark_spots": [
        {"ingredient": "Vitamin C", "why": "Fades discoloration and evens tone over time.",
         "use": "AM", "frequency": "Daily"},
        {"ingredient": "Alpha Arbutin", "why": "Targets stubborn dark spots directly.",
         "use": "PM", "frequency": "Daily"},
    ],
    "dry_skin": [
        {"ingredient": "Hyaluronic Acid", "why": "Attracts and binds water to replenish dry areas.",
         "use": "AM & PM", "frequency": "Daily"},
        {"ingredient": "Ceramides", "why": "Fortifies the lipid barrier to prevent transepidermal moisture loss.",
         "use": "PM", "frequency": "Daily"},
    ],
    "oily_skin": [
        {"ingredient": "Niacinamide", "why": "Controls excess sebum production and refines texture.",
         "use": "AM & PM", "frequency": "Daily"},
        {"ingredient": "Zinc PCA", "why": "Regulates sebum production without drying skin.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "large_pores": [
        {"ingredient": "Niacinamide", "why": "Refines the look of enlarged pores and improves elasticity.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "eyebags": [
        {"ingredient": "Caffeine", "why": "De-puffs and constricts blood vessels under the eyes.",
         "use": "AM", "frequency": "Daily"},
        {"ingredient": "Peptides", "why": "Firms delicate under-eye skin to reduce sagging.",
         "use": "PM", "frequency": "Daily"},
    ],
    "dark_circles": [
        {"ingredient": "Caffeine", "why": "De-puffs and brightens the under-eye area.",
         "use": "AM", "frequency": "Daily"},
        {"ingredient": "Peptides", "why": "Firms thin under-eye skin over time.",
         "use": "PM", "frequency": "Daily"},
    ],
    "redness": [
        {"ingredient": "Azelaic Acid", "why": "Calms redness and evens out skin tone.",
         "use": "AM or PM", "frequency": "Daily"},
        {"ingredient": "Centella Asiatica", "why": "Soothes and repairs an irritated barrier.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "wrinkles": [
        {"ingredient": "Retinol", "why": "Speeds up cell turnover to soften fine lines and stimulate collagen.",
         "use": "PM", "frequency": "2-3x / week"},
        {"ingredient": "Peptides", "why": "Supports collagen for firmer-looking skin.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "uneven_texture": [
        {"ingredient": "Glycolic Acid (AHA)", "why": "Exfoliates the surface for smoother texture.",
         "use": "PM", "frequency": "1-3x / week"},
    ],
    "dehydration": [
        {"ingredient": "Hyaluronic Acid", "why": "Replenishes water content at the surface.",
         "use": "AM & PM", "frequency": "Daily"},
    ],
    "dullness": [
        {"ingredient": "Vitamin C", "why": "Brightens and restores radiance.",
         "use": "AM", "frequency": "Daily"},
    ],
}


def _normalize(label: str) -> str:
    """Matches YOLO class names to CONCERN_INGREDIENTS keys regardless of
    spacing/casing, e.g. 'Dark-Spots' -> 'dark_spots', 'Skin-Redness' -> 'redness',
    'Englarged-Pores' -> 'large_pores'."""
    k = label.strip().lower().replace(" ", "_").replace("-", "_")
    if k in ("skin_redness", "redness"):
        return "redness"
    if k in ("englarged_pores", "enlarged_pores", "large_pores"):
        return "large_pores"
    if k in ("eyebags", "eye_bags", "dark_circles"):
        return "eyebags"
    return k


def build_recommendations(skin_type: str, concerns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []

    for rec in SKIN_TYPE_BASE.get(_normalize(skin_type), []):
        if rec["ingredient"] not in seen:
            out.append(rec)
            seen.add(rec["ingredient"])

    # sort concerns by confidence so the most confident findings drive the top recs
    for concern in sorted(concerns, key=lambda c: c.get("confidence", 0), reverse=True):
        norm_key = _normalize(concern.get("label", ""))
        for rec in CONCERN_INGREDIENTS.get(norm_key, []):
            if rec["ingredient"] not in seen:
                out.append(rec)
                seen.add(rec["ingredient"])

    return out
