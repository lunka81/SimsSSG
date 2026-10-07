from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from demo.models.employee_test import Permission
from demo.models.employee_test_log import EmployeeTestLog
from demo.schemas.employee_log_schema import EmployeeLogResponse
from datetime import datetime

class EmployeeCreate(BaseModel):
    name: str
    permission: Permission
    description: str | None = None
    # The image is sent as a data URL: "data:image/jpeg;base64,..."
    img: str


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    permission: Permission
    description: str | None

class EmployeeDetailResponse(EmployeeResponse):
    employee_logs: list[EmployeeLogResponse] = Field(
        default_factory=list
    )