"""CPU inference for the two trained nypiel models."""
import io
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image

SKIN_TYPES = ["combination", "dry", "normal", "oily"]
CONCERN_CLASSES = [
    "acne", "dark_spots", "wrinkles", "redness", "large_pores",
    "dark_circles", "blackheads", "uneven_texture", "dehydration", "dullness",
]

ROOT_DIR = Path(__file__).resolve().parents[2]
WEIGHTS_DIR = ROOT_DIR / "backend" / "weights"
SKIN_TYPE_MODEL_PATH = WEIGHTS_DIR / "nypiel_skin_type_model.pth"
CONCERN_MODEL_PATH = WEIGHTS_DIR / "best.pt"

_skin_type_model: Any = None
_concern_model: Any = None


def _is_lfs_pointer(path: Path) -> bool:
    try:
        header = path.read_bytes()[:200].decode("utf-8", errors="ignore")
    except OSError:
        return False
    return header.startswith("version https://git-lfs.github.com/spec/v1")


def validate_model_files() -> Tuple[List[str], List[str]]:
    """Return missing model paths and paths that are Git LFS pointers."""
    missing = []
    lfs_pointers = []
    for path in (SKIN_TYPE_MODEL_PATH, CONCERN_MODEL_PATH):
        relative_path = path.relative_to(ROOT_DIR).as_posix()
        if not path.is_file():
            missing.append(relative_path)
        elif _is_lfs_pointer(path):
            lfs_pointers.append(relative_path)
    return missing, lfs_pointers


def load_models():
    """Load both trained models once, always mapping them to CPU."""
    global _skin_type_model, _concern_model

    missing, lfs_pointers = validate_model_files()
    if missing:
        raise FileNotFoundError(
            "Required model file(s) are missing: " + ", ".join(missing)
        )
    if lfs_pointers:
        raise RuntimeError(
            "Required model file(s) are Git LFS pointer files, not downloaded "
            "weights: " + ", ".join(lfs_pointers)
        )

    try:
        import torch
        from torchvision.models import resnet18
        from ultralytics import YOLO

        checkpoint = torch.load(
            str(SKIN_TYPE_MODEL_PATH),
            map_location="cpu",
            weights_only=False,
        )
        if not isinstance(checkpoint, dict):
            raise TypeError("nypiel_skin_type_model.pth is not a checkpoint dictionary.")

        classes = checkpoint.get("classes")
        class_to_idx = checkpoint.get("class_to_idx")
        expected_classes = ["combination", "dry", "normal", "oily"]
        if classes != expected_classes or class_to_idx != {
            label: index for index, label in enumerate(expected_classes)
        }:
            raise ValueError(
                "The skin checkpoint class metadata does not match the expected "
                f"training order {expected_classes!r}."
            )

        state_dict = checkpoint.get("model_state_dict")
        if not isinstance(state_dict, dict):
            raise TypeError("nypiel_skin_type_model.pth has no model_state_dict.")

        skin_model = resnet18(weights=None, num_classes=len(expected_classes))
        skin_model.load_state_dict(state_dict, strict=True)

        _skin_type_model = skin_model.to("cpu").eval()
        _concern_model = YOLO(str(CONCERN_MODEL_PATH), task="detect")
        _concern_model.to("cpu")
    except Exception as exc:
        _skin_type_model = None
        _concern_model = None
        raise RuntimeError(f"Unable to load the trained models on CPU: {exc}") from exc

    return _skin_type_model, _concern_model


def _require_models() -> Tuple[Any, Any]:
    if _skin_type_model is None or _concern_model is None:
        load_models()
    return _skin_type_model, _concern_model


def predict_skin_type(image_bytes: bytes) -> Dict[str, Any]:
    """Return ``{"label": str, "confidence": float}``."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    skin_model, _ = _require_models()

    import torch
    from torchvision import transforms

    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    with torch.inference_mode():
        output = skin_model(preprocess(image).unsqueeze(0))
        logits = output[0] if isinstance(output, (tuple, list)) else output
        probabilities = torch.softmax(logits, dim=1)[0]
        index = int(torch.argmax(probabilities).item())

    if index >= len(SKIN_TYPES):
        raise ValueError(f"Skin model returned unsupported class index {index}.")
    return {"label": SKIN_TYPES[index], "confidence": float(probabilities[index].item())}


def predict_skin_concerns(image_bytes: bytes) -> List[Dict[str, Any]]:
    """Return concern detections with normalized ``[x, y, w, h]`` boxes."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    _, concern_model = _require_models()
    results = concern_model.predict(source=image, device="cpu", verbose=False)
    if not results or results[0].boxes is None:
        return []

    result = results[0]
    names = result.names
    width, height = image.size
    detections = []
    for box, confidence, class_id in zip(
        result.boxes.xyxy.cpu().tolist(),
        result.boxes.conf.cpu().tolist(),
        result.boxes.cls.cpu().tolist(),
    ):
        x1, y1, x2, y2 = box
        class_index = int(class_id)
        if isinstance(names, dict):
            label = names.get(class_index, str(class_index))
        elif class_index < len(names):
            label = names[class_index]
        else:
            label = str(class_index)
        detections.append({
            "label": label,
            "confidence": float(confidence),
            "box": [
                max(0.0, x1 / width),
                max(0.0, y1 / height),
                max(0.0, (x2 - x1) / width),
                max(0.0, (y2 - y1) / height),
            ],
        })
    return detections