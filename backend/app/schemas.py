import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class Concern(BaseModel):
    label: str
    confidence: float
    box: Optional[List[float]] = None  # [x, y, w, h] as fractions of image size (0-1)


class Recommendation(BaseModel):
    ingredient: str
    why: str
    use: str  # e.g. "AM" / "PM" / "AM & PM"
    frequency: str


class ScanResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime.datetime
    image_path: str
    skin_type: str
    skin_type_confidence: float
    concerns: List[Concern]
    recommendations: List[Recommendation]


class ChatMessage(BaseModel):
    message: str
    scan_id: Optional[int] = None  # let the bot ground its answer in a specific saved result


class ChatReply(BaseModel):
    reply: str
