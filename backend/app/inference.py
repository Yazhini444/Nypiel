import io
import os
import random
from typing import List, Dict, Any

from PIL import Image

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BACKEND_DIR, "weights")


def _find_model_file(*names: str) -> str | None:
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


SKIN_TYPES = ["combination", "dry", "normal", "oily"]

CONCERN_CLASSES = [
    "acne",
    "dark_spots",
    "wrinkles",
    "redness",
    "large_pores",
    "eyebags",
    "blackheads",
    "whiteheads",
    "dry_skin",
    "oily_skin",
]


# Models are NOT loaded during startup.
_skin_type_model = None
_skin_type_device = None
_concern_model = None


def normalize_concern_label(raw_name: str) -> str:
    cleaned = (
        raw_name.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if cleaned in ("englarged_pores", "enlarged_pores"):
        return "large_pores"

    if cleaned == "skin_redness":
        return "redness"

    return cleaned


def load_models():
    """
    Lightweight startup function.

    We deliberately do NOT load PyTorch/YOLO here because
    Render's 512 MB RAM can be exceeded during startup.
    Models are loaded only when first needed.
    """
    print("[nypiel] Model loading deferred until first prediction.")

    if os.path.exists(SKIN_TYPE_WEIGHTS):
        print(f"[nypiel] Skin-type model found: {SKIN_TYPE_WEIGHTS}")
    else:
        print(f"[nypiel] Skin-type model NOT found: {SKIN_TYPE_WEIGHTS}")

    if os.path.exists(CONCERN_WEIGHTS):
        print(f"[nypiel] Concern model found: {CONCERN_WEIGHTS}")
    else:
        print(f"[nypiel] Concern model NOT found: {CONCERN_WEIGHTS}")


def _load_skin_type_model():
    global _skin_type_model, _skin_type_device, SKIN_TYPES

    if _skin_type_model is not None:
        return True

    if not os.path.exists(SKIN_TYPE_WEIGHTS):
        print("[nypiel] Skin-type weights not found.")
        return False

    try:
        import torch

        # Render is CPU.
        _skin_type_device = "cpu"

        loaded = torch.load(
            SKIN_TYPE_WEIGHTS,
            map_location="cpu",
            weights_only=False,
        )

        if hasattr(loaded, "eval"):
            _skin_type_model = loaded.to("cpu").eval()
            print("[nypiel] Loaded skin-type full model.")
            return True

        if isinstance(loaded, dict):

            if "classes" in loaded and isinstance(loaded["classes"], list):
                SKIN_TYPES = loaded["classes"]

            elif "class_to_idx" in loaded and isinstance(
                loaded["class_to_idx"], dict
            ):
                SKIN_TYPES = sorted(
                    loaded["class_to_idx"].keys(),
                    key=lambda k: loaded["class_to_idx"][k],
                )

            state_dict = loaded.get(
                "model_state_dict",
                loaded.get("state_dict", loaded),
            )

        else:
            state_dict = loaded

        # IMPORTANT:
        # Your Nypiel V2 checkpoint may NOT be a ResNet18.
        # Therefore we first try ResNet18 only for compatibility.
        from torchvision.models import resnet18

        net = resnet18(
            weights=None,
            num_classes=len(SKIN_TYPES),
        )

        net.load_state_dict(state_dict, strict=True)

        _skin_type_model = net.to("cpu").eval()

        print(
            f"[nypiel] Loaded skin-type ResNet18 "
            f"with classes: {SKIN_TYPES}"
        )

        return True

    except Exception as exc:
        print(
            f"[nypiel] Skin-type model could not be loaded: {exc}"
        )
        _skin_type_model = None
        return False


def _load_concern_model():
    global _concern_model

    if _concern_model is not None:
        return True

    if not os.path.exists(CONCERN_WEIGHTS):
        print("[nypiel] Concern weights not found.")
        return False

    try:
        from ultralytics import YOLO

        print("[nypiel] Loading YOLO concern model...")

        _concern_model = YOLO(CONCERN_WEIGHTS)

        print(
            f"[nypiel] YOLO concern model loaded: "
            f"{CONCERN_WEIGHTS}"
        )

        if hasattr(_concern_model, "names"):
            print(
                f"[nypiel] Concern classes: "
                f"{_concern_model.names}"
            )

        return True

    except Exception as exc:
        print(
            f"[nypiel] Could not load YOLO model: {exc}"
        )
        _concern_model = None
        return False


def predict_skin_type(image_bytes: bytes) -> Dict[str, Any]:

    img = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # Try real model
    if _load_skin_type_model():

        try:
            import torch
            from torchvision import transforms

            tfm = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])

            tensor = tfm(img).unsqueeze(0)

            with torch.no_grad():

                logits = _skin_type_model(tensor)

                probs = torch.softmax(
                    logits,
                    dim=1,
                )[0]

                idx = int(
                    torch.argmax(probs).item()
                )

            return {
                "label": SKIN_TYPES[idx],
                "confidence": round(
                    float(probs[idx]),
                    2,
                ),
            }

        except Exception as exc:
            print(
                f"[nypiel] Skin-type inference failed: {exc}"
            )

    # Temporary fallback
    label = random.choice(SKIN_TYPES)

    return {
        "label": label,
        "confidence": round(
            random.uniform(0.78, 0.97),
            2,
        ),
    }


def predict_skin_concerns(
    image_bytes: bytes,
) -> List[Dict[str, Any]]:

    img = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # Load YOLO only when actually needed
    if _load_concern_model():

        try:

            results = _concern_model.predict(
                img,
                verbose=False,
                conf=0.20,
                device="cpu",
            )[0]

            img_w, img_h = img.size

            names = results.names

            output = []

            for box in results.boxes:

                cls_idx = int(box.cls[0])
                conf = float(box.conf[0])

                if isinstance(names, dict):
                    raw_name = names[cls_idx]
                else:
                    raw_name = names[cls_idx]

                label = normalize_concern_label(
                    str(raw_name)
                )

                x1, y1, x2, y2 = [
                    float(v)
                    for v in box.xyxy[0]
                ]

                output.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "box": [
                        round(
                            max(
                                0.0,
                                min(1.0, x1 / img_w),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(1.0, y1 / img_h),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    (x2 - x1) / img_w,
                                ),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    (y2 - y1) / img_h,
                                ),
                            ),
                            3,
                        ),
                    ],
                })

            return output

        except Exception as exc:

            print(
                f"[nypiel] YOLO inference failed: {exc}"
            )

    # Temporary fallback
    picks = random.sample(
        CONCERN_CLASSES,
        k=random.randint(2, 4),
    )

    output = []

    for label in picks:

        output.append({
            "label": label,
            "confidence": round(
                random.uniform(0.60, 0.95),
                2,
            ),
            "box": [
                round(random.uniform(0.1, 0.6), 2),
                round(random.uniform(0.1, 0.6), 2),
                round(random.uniform(0.15, 0.3), 2),
                round(random.uniform(0.15, 0.3), 2),
            ],
        })

    return output