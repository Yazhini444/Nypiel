"""
Wires in your two trained models:

  weights/skin_type.pt      -> Model 1: single-label classifier
                                (dry / oily / combination / normal)
  weights/skin_concerns.pt  -> Model 2: your best.pt from Ultralytics YOLO
                                (multi-label detector, up to 10 concern
                                classes, each with a bounding box)

Drop your two files into backend/weights/ using those exact names (or
change the paths in load_models() below), then restart the server. If a
file isn't there, this module quietly falls back to mock predictions so
the rest of the app keeps working.
"""
import io
import os
import random
from typing import List, Dict, Any

from PIL import Image

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BACKEND_DIR, "weights")


def _find_model_file(*names: str) -> str | None:
    """Prefer files in the backend root (the project uses those names) and
    fall back to backend/weights for older setups."""
    for base in (BACKEND_DIR, WEIGHTS_DIR):
        for name in names:
            path = os.path.join(base, name)
            if os.path.exists(path):
                return path
    return None


SKIN_TYPE_WEIGHTS = _find_model_file(
    "nypiel_skin_type_model.pth",
    "skin_type_model.pth",
    "skin_type.pt",
    "skin_type.pth",
) or os.path.join(WEIGHTS_DIR, "skin_type.pt")
CONCERN_WEIGHTS = _find_model_file(
    "best.pt",
    "skin_concerns.pt",
    "skin_concern.pt",
    "concerns.pt",
) or os.path.join(WEIGHTS_DIR, "skin_concerns.pt")

# Default classes from the trained checkpoint: {'combination': 0, 'dry': 1, 'normal': 2, 'oily': 3}
SKIN_TYPES = ["combination", "dry", "normal", "oily"]

# Fallback labels only — YOLO stores its own class names inside best.pt
# (results.names), so this list is just used for the mock predictor below.
CONCERN_CLASSES = [
    "acne", "dark_spots", "wrinkles", "redness", "large_pores",
    "eyebags", "blackheads", "whiteheads", "dry_skin", "oily_skin",
]

_skin_type_model = None
_skin_type_device = None
_concern_model = None  # ultralytics YOLO object


def normalize_concern_label(raw_name: str) -> str:
    """Standardizes YOLO class names (e.g. 'Dark-Spots' -> 'dark_spots',
    'Englarged-Pores' -> 'large_pores', 'Skin-Redness' -> 'redness')."""
    cleaned = raw_name.strip().lower().replace("-", "_").replace(" ", "_")
    if cleaned in ("englarged_pores", "enlarged_pores"):
        return "large_pores"
    if cleaned in ("skin_redness",):
        return "redness"
    return cleaned


def load_models():
    """Called once at server startup (see main.py)."""
    global _skin_type_model, _skin_type_device, _concern_model, SKIN_TYPES

    # --- Model 2: skin concerns (YOLO best.pt) ---
    if os.path.exists(CONCERN_WEIGHTS):
        try:
            from ultralytics import YOLO
            _concern_model = YOLO(CONCERN_WEIGHTS)
            print(f"[nypiel] Loaded concern model from {CONCERN_WEIGHTS}")
            if hasattr(_concern_model, "names"):
                print(f"[nypiel] Concern classes: {_concern_model.names}")
        except Exception as exc:
            _concern_model = None
            print(
                f"[nypiel] Could not load concern model from {CONCERN_WEIGHTS}. "
                f"Falling back to mock predictions. Details: {exc}"
            )
    else:
        print(f"[nypiel] No concern model at {CONCERN_WEIGHTS} — using mock predictions.")

    # --- Model 1: skin type classifier (ResNet18) ---
    if os.path.exists(SKIN_TYPE_WEIGHTS):
        import torch
        _skin_type_device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            loaded = torch.load(SKIN_TYPE_WEIGHTS, map_location=_skin_type_device, weights_only=False)
        except Exception as exc:
            print(f"[nypiel] Failed to load skin-type model at {SKIN_TYPE_WEIGHTS}: {exc}")
            loaded = None

        if loaded is None:
            print(f"[nypiel] Skin-type model found but could not be loaded — using mock predictions.")
        elif hasattr(loaded, "eval"):
            # Case A: the whole model was pickled with torch.save(model)
            _skin_type_model = loaded.to(_skin_type_device).eval()
            print(f"[nypiel] Loaded skin-type model (full model) from {SKIN_TYPE_WEIGHTS}")
        else:
            # Case B: dict containing model_state_dict, classes, and class_to_idx
            if isinstance(loaded, dict):
                if "classes" in loaded and isinstance(loaded["classes"], list):
                    SKIN_TYPES = loaded["classes"]
                elif "class_to_idx" in loaded and isinstance(loaded["class_to_idx"], dict):
                    SKIN_TYPES = sorted(loaded["class_to_idx"].keys(), key=lambda k: loaded["class_to_idx"][k])

                state_dict = loaded.get("model_state_dict", loaded.get("state_dict", loaded))
            else:
                state_dict = loaded

            try:
                from torchvision.models import resnet18

                net = resnet18(weights=None, num_classes=len(SKIN_TYPES))
                net.load_state_dict(state_dict, strict=True)
                _skin_type_model = net.to(_skin_type_device).eval()
                print(
                    f"[nypiel] Loaded skin-type model state_dict into ResNet18 ({len(SKIN_TYPES)} classes: {SKIN_TYPES}) from {SKIN_TYPE_WEIGHTS}"
                )
            except Exception as exc:
                print(
                    f"[nypiel] Skin-type checkpoint found at {SKIN_TYPE_WEIGHTS}, but could not load state_dict: {exc}. "
                    f"Trying non-strict loading..."
                )
                try:
                    from torchvision.models import resnet18
                    net = resnet18(weights=None, num_classes=len(SKIN_TYPES))
                    net.load_state_dict(state_dict, strict=False)
                    _skin_type_model = net.to(_skin_type_device).eval()
                    print(f"[nypiel] Loaded skin-type model with non-strict state_dict from {SKIN_TYPE_WEIGHTS}")
                except Exception as exc2:
                    print(f"[nypiel] Failed to load skin-type model: {exc2}. Using mock fallback.")
                    _skin_type_model = None
    else:
        print(f"[nypiel] No skin-type model at {SKIN_TYPE_WEIGHTS} — using mock predictions.")


def _preprocess_for_classifier(img: Image.Image):
    """Standard ImageNet-style preprocessing for ResNet-18."""
    from torchvision import transforms

    tfm = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return tfm(img).unsqueeze(0).to(_skin_type_device)


def predict_skin_type(image_bytes: bytes) -> Dict[str, Any]:
    """Returns {"label": str, "confidence": float}."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if _skin_type_model is not None:
        import torch
        with torch.no_grad():
            from torchvision import transforms
            tfm = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            tensor = tfm(img).unsqueeze(0).to(_skin_type_device)
            logits = _skin_type_model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            idx = int(torch.argmax(probs).item())
        return {"label": SKIN_TYPES[idx], "confidence": round(float(probs[idx]), 2)}

    # Mock fallback so the API is runnable before the model is plugged in.
    label = random.choice(SKIN_TYPES)
    return {"label": label, "confidence": round(random.uniform(0.78, 0.97), 2)}


def predict_skin_concerns(image_bytes: bytes) -> List[Dict[str, Any]]:
    """Returns a list of {"label": str, "confidence": float, "box": [x,y,w,h]}.
    Box coordinates are fractions (0-1) of image width/height, so the
    frontend can position markers regardless of the rendered image size."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if _concern_model is not None:
        try:
            results = _concern_model.predict(img, verbose=False, conf=0.20)[0]
            img_w, img_h = img.size
            names = results.names  # class index -> label, baked into best.pt

            out = []
            for box in results.boxes:
                cls_idx = int(box.cls[0])
                conf = float(box.conf[0])
                raw_name = names[cls_idx] if isinstance(names, dict) else names[cls_idx]
                norm_label = normalize_concern_label(str(raw_name))
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                out.append({
                    "label": norm_label,
                    "confidence": round(conf, 2),
                    "box": [
                        round(max(0.0, min(1.0, x1 / img_w)), 3),
                        round(max(0.0, min(1.0, y1 / img_h)), 3),
                        round(max(0.0, min(1.0, (x2 - x1) / img_w)), 3),
                        round(max(0.0, min(1.0, (y2 - y1) / img_h)), 3),
                    ],
                })
            return out
        except Exception as exc:
            print(f"[nypiel] Concern inference failed at runtime: {exc}. Falling back to mock predictions.")

    # Mock fallback: pick 2-4 plausible concerns with fake boxes.
    picks = random.sample(CONCERN_CLASSES, k=random.randint(2, 4))
    results = []
    for label in picks:
        results.append({
            "label": label,
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "box": [
                round(random.uniform(0.1, 0.6), 2),
                round(random.uniform(0.1, 0.6), 2),
                round(random.uniform(0.15, 0.3), 2),
                round(random.uniform(0.15, 0.3), 2),
            ],
        })
    return results
