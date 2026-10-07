from datetime import datetime
import os
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field, FiniteFloat, field_validator
from sqlalchemy.orm import Session

from demo.db.database import get_session
from demo.services.recognition_services import identify_employee


recognition_router = APIRouter(
    prefix="/recognition",
    tags=["Recognition"],
)


class RecognitionRequest(BaseModel):
    camera_id: str
    timestamp: datetime
    detection_confidence: FiniteFloat = Field(ge=0, le=1)
    face_width: int = Field(gt=0)
    face_height: int = Field(gt=0)
    embedding: list[FiniteFloat] = Field(
        min_length=128,
        max_length=128,
    )

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, values):
        if not any(value != 0 for value in values):
            raise ValueError("Embedding får inte vara en nollvektor.")

        return values


class RecognitionResponse(BaseModel):
    approved: bool
    employee_uuid: UUID | None
    name: str | None
    similarity: float | None
    reason: str


@recognition_router.post(
    "/identify",
    response_model=RecognitionResponse,
)
def identify(
    payload: RecognitionRequest,
    session: Session = Depends(get_session),
    x_api_key: str | None = Header(default=None),
):
    expected_key = os.environ["DEVICE_API_KEY"]

    if x_api_key is None or not secrets.compare_digest(
        x_api_key,
        expected_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    return identify_employee(
        session=session,
        embedding=payload.embedding,
    )