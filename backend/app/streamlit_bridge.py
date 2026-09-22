"""Streamlit-side request handlers for the embedded React application."""
import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import streamlit as st

from .inference import predict_skin_concerns, predict_skin_type
from .recommendations import build_recommendations

LOGGER = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-3.5-flash-lite"


class BridgeError(Exception):
    """An expected request error safe to return to the React component."""


def _api_key():
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.getenv("GEMINI_API_KEY")


def _data_url_bytes(data_url: str) -> bytes:
    if not isinstance(data_url, str) or "," not in data_url:
        raise BridgeError("Please select a valid image.")
    header, encoded = data_url.split(",", 1)
    if not header.startswith("data:image/"):
        raise BridgeError("Please select a JPEG, PNG, or WEBP image.")
    try:
        return base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise BridgeError("The selected image could not be read.") from exc


def _image_data_url(image: str) -> str:
    return image


def _deduplicate_concerns(concerns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best_by_label: Dict[str, Dict[str, Any]] = {}
    for concern in concerns:
        label = str(concern.get("label", "")).strip().lower().replace("-", "_")
        if not label:
            continue
        candidate = {**concern, "label": label}
        current = best_by_label.get(label)
        if current is None or candidate.get("confidence", 0) > current.get("confidence", 0):
            best_by_label[label] = candidate
    return sorted(best_by_label.values(), key=lambda item: item.get("confidence", 0), reverse=True)


def _user():
    return st.session_state.get("nypiel_bridge_user")


def _require_user():
    user = _user()
    if not user:
        raise BridgeError("Please log in to continue.")
    return user


def _public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": user["id"], "email": user["email"], "name": user.get("name")}


def _signup(payload: Dict[str, Any]) -> Dict[str, Any]:
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not email or len(password) < 8:
        raise BridgeError("Enter a valid email and a password of at least 8 characters.")
    users = st.session_state.setdefault("nypiel_bridge_users", {})
    if email in users:
        raise BridgeError("An account with this email already exists.")
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = {"id": len(users) + 1, "email": email, "name": payload.get("name"), "password_hash": password_hash}
    users[email] = user
    st.session_state["nypiel_bridge_user"] = user
    return {"access_token": f"streamlit-session-{user['id']}", "token_type": "bearer", "user": _public_user(user)}


def _login(payload: Dict[str, Any]) -> Dict[str, Any]:
    email = str(payload.get("email", "")).strip().lower()
    users = st.session_state.setdefault("nypiel_bridge_users", {})
    user = users.get(email)
    password_hash = hashlib.sha256(str(payload.get("password", "")).encode("utf-8")).hexdigest()
    if not user or not hmac.compare_digest(user.get("password_hash", ""), password_hash):
        raise BridgeError("Incorrect email or password.")
    st.session_state["nypiel_bridge_user"] = user
    return {"access_token": f"streamlit-session-{user['id']}", "token_type": "bearer", "user": _public_user(user)}


def _analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    _require_user()
    image = payload.get("image")
    image_bytes = _data_url_bytes(image)
    skin_result = predict_skin_type(image_bytes)
    concerns = _deduplicate_concerns(predict_skin_concerns(image_bytes))
    recommendations = build_recommendations(skin_result["label"], concerns)
    scans = st.session_state.setdefault("nypiel_bridge_scans", [])
    scan = {
        "id": len(scans) + 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image_path": _image_data_url(image),
        "skin_type": skin_result["label"],
        "skin_type_confidence": skin_result["confidence"],
        "concerns": concerns,
        "recommendations": recommendations,
    }
    if payload.get("save", True):
        scans.insert(0, scan)
    st.session_state["nypiel_bridge_analysis"] = scan
    return scan


def _ask(payload: Dict[str, Any]) -> Dict[str, str]:
    _require_user()
    api_key = _api_key()
    if not api_key:
        raise BridgeError("Gemini API key is not configured. Please add GEMINI_API_KEY to your environment or Streamlit Secrets.")
    try:
        from google import genai
        from google.genai import types

        history = st.session_state.setdefault("nypiel_bridge_chat", [])
        history.append({"role": "user", "content": str(payload.get("message", ""))})
        analysis = st.session_state.get("nypiel_bridge_analysis")
        context = "No Nypiel image analysis is available."
        if analysis:
            labels = ", ".join(item["label"].replace("_", " ") for item in analysis["concerns"]) or "None detected"
            ingredients = ", ".join(item["ingredient"] for item in analysis["recommendations"]) or "None available"
            context = f"Skin type: {analysis['skin_type']}\nDetected concerns: {labels}\nRecommendations: {ingredients}"
        contents = [
            types.Content(role=item["role"], parts=[types.Part.from_text(text=item["content"])])
            for item in history
        ]
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Nypiel, a practical skincare assistant. Give clear, useful skincare guidance "
                    "without diagnosing medical conditions. Recommend a dermatologist for serious or persistent concerns.\n\n"
                    f"Current Nypiel analysis:\n{context}"
                ),
            ),
        )
        if not response.text:
            raise BridgeError("Gemini returned an empty response.")
        history.append({"role": "model", "content": response.text})
        return {"reply": response.text}
    except BridgeError:
        raise
    except Exception as exc:
        safe_message = str(exc).replace(api_key, "[REDACTED]")
        LOGGER.exception("Gemini bridge request failed: %s", safe_message)
        raise BridgeError("Gemini could not answer right now. Please try again.") from exc


def handle_bridge_request(request: Dict[str, Any]) -> Any:
    action = request.get("action")
    payload = request.get("payload") or {}
    LOGGER.info("Handling Streamlit bridge action=%s; authenticated=%s", action, bool(_user()))
    handlers = {
        "signup": _signup,
        "login": _login,
        "logout": _logout,
        "me": lambda _: _public_user(_require_user()),
        "analyze": _analyze,
        "history": lambda _: list(st.session_state.get("nypiel_bridge_scans", [])),
        "getScan": lambda data: next((scan for scan in st.session_state.get("nypiel_bridge_scans", []) if scan["id"] == data.get("id")), None),
        "deleteScan": lambda data: _delete_scan(data.get("id")),
        "ask": _ask,
        "reset": _reset,
    }
    if action not in handlers:
        raise BridgeError(f"Unsupported bridge action: {action}")
    return handlers[action](payload)


def _delete_scan(scan_id: Any) -> Dict[str, bool]:
    scans = st.session_state.get("nypiel_bridge_scans", [])
    st.session_state["nypiel_bridge_scans"] = [scan for scan in scans if scan["id"] != scan_id]
    return {"ok": True}


def _reset(_: Dict[str, Any]) -> Dict[str, bool]:
    for key in ("nypiel_bridge_analysis", "nypiel_bridge_scans", "nypiel_bridge_chat", "nypiel_bridge_user"):
        st.session_state.pop(key, None)
    return {"ok": True}


def _logout(_: Dict[str, Any]) -> Dict[str, bool]:
    for key in ("nypiel_bridge_user", "nypiel_bridge_analysis", "nypiel_bridge_chat"):
        st.session_state.pop(key, None)
    return {"ok": True}