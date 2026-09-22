from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth, chatbot
from ..database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=schemas.ChatReply)
def ask(
    payload: schemas.ChatMessage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    reply = chatbot.answer(payload.message, db, current_user.id, payload.scan_id)
    return schemas.ChatReply(reply=reply)
