import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth, inference, recommendations
from ..database import get_db

router = APIRouter(prefix="/scan", tags=["scan"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/analyze", response_model=schemas.ScanResultOut)
async def analyze(
    file: UploadFile = File(...),
    save: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Please upload a JPEG, PNG, or WEBP image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    # --- Model 1: skin type ---
    skin_type_result = inference.predict_skin_type(image_bytes)
    # --- Model 2: skin concerns (multi-label) ---
    concerns = inference.predict_skin_concerns(image_bytes)
    # --- Recommendation engine, built from both model outputs ---
    recs = recommendations.build_recommendations(skin_type_result["label"], concerns)

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)

    result = models.ScanResult(
        owner_id=current_user.id,
        image_path=f"/uploads/{filename}",
        skin_type=skin_type_result["label"],
        skin_type_confidence=skin_type_result["confidence"],
        concerns=concerns,
        recommendations=recs,
    )

    if save:
        db.add(result)
        db.commit()
        db.refresh(result)
    else:
        # Preview mode: run inference but don't persist. Give it a transient id.
        result.id = 0
        result.created_at = __import__("datetime").datetime.utcnow()

    return result


@router.get("/history", response_model=List[schemas.ScanResultOut])
def history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.ScanResult)
        .filter(models.ScanResult.owner_id == current_user.id)
        .order_by(models.ScanResult.created_at.desc())
        .all()
    )


@router.get("/{scan_id}", response_model=schemas.ScanResultOut)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    scan = (
        db.query(models.ScanResult)
        .filter(models.ScanResult.id == scan_id, models.ScanResult.owner_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    scan = (
        db.query(models.ScanResult)
        .filter(models.ScanResult.id == scan_id, models.ScanResult.owner_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    db.delete(scan)
    db.commit()
    return {"ok": True}
