from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EmployeeLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    employee_uuid: UUID
    timestamp: datetime
    approved: bool