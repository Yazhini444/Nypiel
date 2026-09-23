"""Streamlit-side request handlers for the embedded React application.

Persistence note:
Streamlit Community Cloud local SQLite storage is ephemeral across container
recreation. The SQLite database at project root persists accounts across
Streamlit restarts and sessions within the local environment and active container,
but permanent multi-host cloud storage requires an external database (e.g. PostgreSQL).
"""
import base64
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

import streamlit as st
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from . import models
from .database import Base, SessionLocal, engine
from .inference import predict_skin_concerns, predict_skin_type
from .passwords import hash_password, verify_password
from .recommendations import build_recommendations

LOGGER = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-3.5-flash-lite"
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

Base.metadata.create_all(bind=engine)


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


def _normalize_email(value: Any) -> str:
    email = str(value or "").strip().lower()
    if not email or not EMAIL_REGEX.match(email):
        raise BridgeError("Enter a valid email address.")
    return email


def _stored_user(user: models.User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "password_hash": user.hashed_password,
        "created_at": user.created_at,
    }


def get_auth_diagnostics(email: str = None) -> Dict[str, Any]:
    """Report database and user status without exposing any sensitive credentials."""
    from sqlalchemy import inspect
    db_url = str(engine.url)
    users_table_exists = False
    user_count = 0
    user_found = False
    normalized_email = email.strip().lower() if email else None

    try:
        inspector = inspect(engine)
        users_table_exists = "users" in inspector.get_table_names()
        if users_table_exists:
            db = SessionLocal()
            try:
                user_count = db.query(models.User).count()
                if normalized_email:
                    match = db.query(models.User).filter(func.lower(models.User.email) == normalized_email).first()
                    user_found = bool(match)
            finally:
                db.close()
    except Exception as exc:
        LOGGER.error("Auth diagnostics check failed: %s", exc)

    diag = {
        "database_path": db_url,
        "users_table_exists": users_table_exists,
        "user_count": user_count,
        "searched_email": normalized_email,
        "user_found": user_found,
    }
    LOGGER.info("Auth diagnostics: %s", diag)
    return diag


def _find_user(email: str) -> Dict[str, Any] | None:
    db = SessionLocal()
    try:
        norm_email = email.strip().lower()
        user = db.query(models.User).filter(func.lower(models.User.email) == norm_email).first()
        return _stored_user(user) if user else None
    finally:
        db.close()


def _get_user_count() -> int:
    db = SessionLocal()
    try:
        return db.query(models.User).count()
    except Exception:
        return 0
    finally:
        db.close()


def _upgrade_user_password(user_id: int, password: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.hashed_password = hash_password(password)
            db.commit()
            LOGGER.info("Upgraded legacy password hash to bcrypt for user_id=%s", user_id)
    except Exception as exc:
        db.rollback()
        LOGGER.error("Failed to upgrade legacy password hash: %s", exc)
    finally:
        db.close()


def _signup(payload: Dict[str, Any]) -> Dict[str, Any]:
    email = _normalize_email(payload.get("email"))
    password = str(payload.get("password", ""))
    db_path = str(engine.url)

    if len(password) < 8:
        print(f"AUTH DB PATH: {db_path}")
        print("AUTH USERS TABLE EXISTS: True")
        print(f"AUTH USER COUNT: {_get_user_count()}")
        print(f"AUTH SIGNUP EMAIL: {email}")
        print("AUTH SIGNUP STATUS: FAILED_PASSWORD_TOO_SHORT")
        LOGGER.warning("Streamlit auth action=signup status=failed_password_too_short db=%s", db_path)
        raise BridgeError("Enter a valid email and a password of at least 8 characters.")

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(func.lower(models.User.email) == email).first()
        if existing:
            print(f"AUTH DB PATH: {db_path}")
            print("AUTH USERS TABLE EXISTS: True")
            print(f"AUTH USER COUNT: {_get_user_count()}")
            print(f"AUTH SIGNUP EMAIL: {email}")
            print("AUTH SIGNUP STATUS: EMAIL_ALREADY_EXISTS")
            LOGGER.info("Streamlit auth action=signup status=email_already_registered matching_user=true db=%s", db_path)
            raise BridgeError("An account with this email already exists.")

        user = models.User(
            email=email,
            name=payload.get("name") or None,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        public_user = {"id": user.id, "email": user.email, "name": user.name}

        user_count = db.query(models.User).count()
        print(f"AUTH DB PATH: {db_path}")
        print("AUTH USERS TABLE EXISTS: True")
        print(f"AUTH USER COUNT: {user_count}")
        print(f"AUTH SIGNUP EMAIL: {email}")
        print("AUTH SIGNUP STATUS: SUCCESS")
        LOGGER.info("Streamlit auth action=signup status=SUCCESS user_id=%s matching_user=false db=%s", user.id, db_path)
    except BridgeError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        LOGGER.info("Streamlit auth action=signup status=integrity_error db=%s", db_path)
        raise BridgeError("An account with this email already exists.") from exc
    finally:
        db.close()

    st.session_state["nypiel_bridge_user"] = public_user
    return {"access_token": f"streamlit-session-{public_user['id']}", "token_type": "bearer", "user": public_user}


def _login(payload: Dict[str, Any]) -> Dict[str, Any]:
    db_path = str(engine.url)
    email_raw = payload.get("email")

    try:
        email = _normalize_email(email_raw)
    except BridgeError:
        email_clean = str(email_raw or "").strip().lower()
        print(f"AUTH DB PATH: {db_path}")
        print("AUTH USERS TABLE EXISTS: True")
        print(f"AUTH USER COUNT: {_get_user_count()}")
        print(f"AUTH LOGIN EMAIL: {email_clean}")
        print("AUTH USER FOUND: False")
        print("AUTH PASSWORD VERIFIED: False")
        LOGGER.info("Streamlit auth action=login status=failed_invalid_email_format db=%s matching_user=false", db_path)
        raise BridgeError("Incorrect email or password.")

    user = _find_user(email)
    user_found = bool(user)
    password = str(payload.get("password", ""))
    password_verified = False

    if user:
        password_verified = verify_password(password, user["password_hash"])
        if password_verified and not user["password_hash"].startswith(("$2a$", "$2b$", "$2y$")):
            _upgrade_user_password(user["id"], password)

    user_count = _get_user_count()
    print(f"AUTH DB PATH: {db_path}")
    print("AUTH USERS TABLE EXISTS: True")
    print(f"AUTH USER COUNT: {user_count}")
    print(f"AUTH LOGIN EMAIL: {email}")
    print(f"AUTH USER FOUND: {user_found}")
    print(f"AUTH PASSWORD VERIFIED: {password_verified}")

    if not user:
        LOGGER.info("Streamlit auth action=login status=USER_NOT_FOUND db=%s matching_user=false", db_path)
        raise BridgeError("Incorrect email or password.")

    if not password_verified:
        LOGGER.info("Streamlit auth action=login status=INVALID_PASSWORD user_id=%s db=%s matching_user=true", user["id"], db_path)
        raise BridgeError("Incorrect email or password.")

    LOGGER.info("Streamlit auth action=login status=SUCCESS user_id=%s db=%s matching_user=true", user["id"], db_path)
    public_user = {"id": user["id"], "email": user["email"], "name": user.get("name")}
    st.session_state["nypiel_bridge_user"] = public_user
    return {"access_token": f"streamlit-session-{user['id']}", "token_type": "bearer", "user": public_user}


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
    LOGGER.info("Handling Streamlit bridge action=%s; authenticated=%s db=%s", action, bool(_user()), engine.url)
    handlers = {
        "signup": _signup,
        "login": _login,
        "logout": _logout,
        "me": lambda _: _public_user(_require_user()),
        "diagnostics": lambda data: get_auth_diagnostics(data.get("email") if isinstance(data, dict) else None),
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
    LOGGER.info("Streamlit auth action=logout db=%s", engine.url)
    return {"ok": True}