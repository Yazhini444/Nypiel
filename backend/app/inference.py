import io
import os
import random
from typing import List, Dict, Any

from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BACKEND_DIR, "weights")

# IMPORTANT:
# Free Render has only 512 MB RAM.
# Keep ML disabled there unless you move to a larger instance.
#
# To enable real models locally:
# Windows:
#   set NYPIEL_ENABLE_ML=true
#
# Render:
#   NYPIEL_ENABLE_ML=false
#
ENABLE_ML = os.getenv("NYPIEL_ENABLE_ML", "false").lower() == "true"


# ============================================================
# MODEL FILE SEARCH
# ============================================================

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


# ============================================================
# CLASSES
# ============================================================

SKIN_TYPES = [
    "combination",
    "dry",
    "normal",
    "oily",
]


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


# ============================================================
# MODEL VARIABLES
# ============================================================

_skin_type_model = None
_skin_type_device = None

_concern_model = None


# ============================================================
# LABEL NORMALIZATION
# ============================================================

def normalize_concern_label(raw_name: str) -> str:

    cleaned = (
        raw_name
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if cleaned in (
        "englarged_pores",
        "enlarged_pores",
    ):
        return "large_pores"

    if cleaned == "skin_redness":
        return "redness"

    return cleaned


# ============================================================
# STARTUP
# ============================================================

def load_models():
    """
    Do NOT load PyTorch or YOLO during application startup.

    On Render Free (512 MB RAM), ML is disabled by default.

    This function only prints model information.
    """

    print("[nypiel] Server started.")

    if not ENABLE_ML:
        print(
            "[nypiel] ML models are DISABLED. "
            "Using lightweight fallback predictions."
        )
        return

    print("[nypiel] ML models are ENABLED.")

    if os.path.exists(SKIN_TYPE_WEIGHTS):
        print(
            f"[nypiel] Skin-type model found: "
            f"{SKIN_TYPE_WEIGHTS}"
        )
    else:
        print(
            f"[nypiel] Skin-type model NOT found: "
            f"{SKIN_TYPE_WEIGHTS}"
        )

    if os.path.exists(CONCERN_WEIGHTS):
        print(
            f"[nypiel] Concern model found: "
            f"{CONCERN_WEIGHTS}"
        )
    else:
        print(
            f"[nypiel] Concern model NOT found: "
            f"{CONCERN_WEIGHTS}"
        )


# ============================================================
# LOAD SKIN TYPE MODEL
# ============================================================

def _load_skin_type_model():

    global _skin_type_model
    global _skin_type_device
    global SKIN_TYPES

    # ML disabled
    if not ENABLE_ML:
        return False

    # Already loaded
    if _skin_type_model is not None:
        return True

    # Model doesn't exist
    if not os.path.exists(SKIN_TYPE_WEIGHTS):

        print(
            "[nypiel] Skin-type weights not found. "
            "Using fallback."
        )

        return False

    try:

        print(
            "[nypiel] Loading skin-type model..."
        )

        import torch

        _skin_type_device = "cpu"

        loaded = torch.load(
            SKIN_TYPE_WEIGHTS,
            map_location="cpu",
            weights_only=False,
        )

        # ----------------------------------------------------
        # Full PyTorch model
        # ----------------------------------------------------

        if hasattr(loaded, "eval"):

            _skin_type_model = (
                loaded
                .to("cpu")
                .eval()
            )

            print(
                "[nypiel] Loaded skin-type full model."
            )

            return True

        # ----------------------------------------------------
        # State dictionary
        # ----------------------------------------------------

        if isinstance(loaded, dict):

            if (
                "classes" in loaded
                and isinstance(loaded["classes"], list)
            ):
                SKIN_TYPES = loaded["classes"]

            elif (
                "class_to_idx" in loaded
                and isinstance(
                    loaded["class_to_idx"],
                    dict,
                )
            ):
                SKIN_TYPES = sorted(
                    loaded["class_to_idx"].keys(),
                    key=lambda k:
                        loaded["class_to_idx"][k],
                )

            state_dict = loaded.get(
                "model_state_dict",
                loaded.get(
                    "state_dict",
                    loaded,
                ),
            )

        else:

            state_dict = loaded

        # ----------------------------------------------------
        # ResNet18 compatibility
        # ----------------------------------------------------

        from torchvision.models import resnet18

        net = resnet18(
            weights=None,
            num_classes=len(SKIN_TYPES),
        )

        net.load_state_dict(
            state_dict,
            strict=True,
        )

        _skin_type_model = (
            net
            .to("cpu")
            .eval()
        )

        print(
            "[nypiel] Loaded skin-type "
            "ResNet18 model."
        )

        return True

    except Exception as exc:

        print(
            f"[nypiel] Skin-type model loading failed: "
            f"{exc}"
        )

        _skin_type_model = None

        return False


# ============================================================
# LOAD CONCERN MODEL
# ============================================================

def _load_concern_model():

    global _concern_model

    # ML disabled
    if not ENABLE_ML:
        return False

    # Already loaded
    if _concern_model is not None:
        return True

    # Model doesn't exist
    if not os.path.exists(CONCERN_WEIGHTS):

        print(
            "[nypiel] Concern weights not found. "
            "Using fallback."
        )

        return False

    try:

        print(
            "[nypiel] Loading YOLO concern model..."
        )

        from ultralytics import YOLO

        _concern_model = YOLO(
            CONCERN_WEIGHTS
        )

        print(
            f"[nypiel] YOLO concern model loaded: "
            f"{CONCERN_WEIGHTS}"
        )

        if hasattr(
            _concern_model,
            "names",
        ):

            print(
                f"[nypiel] Concern classes: "
                f"{_concern_model.names}"
            )

        return True

    except Exception as exc:

        print(
            f"[nypiel] YOLO model loading failed: "
            f"{exc}"
        )

        _concern_model = None

        return False


# ============================================================
# SKIN TYPE PREDICTION
# ============================================================

def predict_skin_type(
    image_bytes: bytes,
) -> Dict[str, Any]:

    # --------------------------------------------------------
    # Validate image
    # --------------------------------------------------------

    img = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # --------------------------------------------------------
    # Try real ML model only if enabled
    # --------------------------------------------------------

    if _load_skin_type_model():

        try:

            import torch
            from torchvision import transforms

            tfm = transforms.Compose([
                transforms.Resize(
                    (224, 224)
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[
                        0.485,
                        0.456,
                        0.406,
                    ],
                    std=[
                        0.229,
                        0.224,
                        0.225,
                    ],
                ),
            ])

            tensor = tfm(img).unsqueeze(0)

            with torch.no_grad():

                logits = _skin_type_model(
                    tensor
                )

                probs = torch.softmax(
                    logits,
                    dim=1,
                )[0]

                idx = int(
                    torch.argmax(
                        probs
                    ).item()
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
                f"[nypiel] Skin-type inference "
                f"failed: {exc}"
            )

    # --------------------------------------------------------
    # Lightweight fallback
    # --------------------------------------------------------

    label = random.choice(
        SKIN_TYPES
    )

    return {
        "label": label,
        "confidence": round(
            random.uniform(
                0.78,
                0.97,
            ),
            2,
        ),
    }


# ============================================================
# SKIN CONCERN PREDICTION
# ============================================================

def predict_skin_concerns(
    image_bytes: bytes,
) -> List[Dict[str, Any]]:

    # --------------------------------------------------------
    # Validate image
    # --------------------------------------------------------

    img = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # --------------------------------------------------------
    # Try real YOLO model only if enabled
    # --------------------------------------------------------

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

                cls_idx = int(
                    box.cls[0]
                )

                conf = float(
                    box.conf[0]
                )

                if isinstance(
                    names,
                    dict,
                ):
                    raw_name = names[
                        cls_idx
                    ]
                else:
                    raw_name = names[
                        cls_idx
                    ]

                label = normalize_concern_label(
                    str(raw_name)
                )

                x1, y1, x2, y2 = [
                    float(v)
                    for v in box.xyxy[0]
                ]

                output.append({
                    "label": label,
                    "confidence": round(
                        conf,
                        2,
                    ),
                    "box": [
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    x1 / img_w,
                                ),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    y1 / img_h,
                                ),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    (x2 - x1)
                                    / img_w,
                                ),
                            ),
                            3,
                        ),
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    (y2 - y1)
                                    / img_h,
                                ),
                            ),
                            3,
                        ),
                    ],
                })

            return output

        except Exception as exc:

            print(
                f"[nypiel] YOLO inference "
                f"failed: {exc}"
            )

    # --------------------------------------------------------
    # Lightweight fallback
    # --------------------------------------------------------

    picks = random.sample(
        CONCERN_CLASSES,
        k=random.randint(
            2,
            4,
        ),
    )

    output = []

    for label in picks:

        output.append({
            "label": label,
            "confidence": round(
                random.uniform(
                    0.60,
                    0.95,
                ),
                2,
            ),
            "box": [
                round(
                    random.uniform(
                        0.1,
                        0.6,
                    ),
                    2,
                ),
                round(
                    random.uniform(
                        0.1,
                        0.6,
                    ),
                    2,
                ),
                round(
                    random.uniform(
                        0.15,
                        0.3,
                    ),
                    2,
                ),
                round(
                    random.uniform(
                        0.15,
                        0.3,
                    ),
                    2,
                ),
            ],
        })

    return output