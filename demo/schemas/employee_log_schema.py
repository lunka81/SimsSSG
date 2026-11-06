from datetime import datetime
from uuid import UUID


from pydantic import BaseModel, ConfigDict, FiniteFloat


class EmployeeLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID    
    employee_uuid: UUID
    match_score: float
    timestamp: datetime
    camera_id: str
    detection_confidence: FiniteFloat
    face_width: int
    face_height: int