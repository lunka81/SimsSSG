from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, FiniteFloat

class ComparisonRequest(BaseModel):
    camera_id: str
    timestamp: datetime
    detection_confidence: FiniteFloat = Field(ge=0, le=1)
    face_width: int = Field(gt=0)
    face_height: int = Field(gt=0)
    embedding: list[FiniteFloat] = Field(
        min_length=128,
        max_length=128,
    )

class ComparisonResponse(BaseModel):
    approved: bool
    employee_uuid: UUID | None = None
    name: str | None = None

class ComparisonDetailResponse(ComparisonResponse):
    #används för 
    confidence: float