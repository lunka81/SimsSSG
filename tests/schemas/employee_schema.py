from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from tests.models.employee_test_log import EmployeeLog

class EmployeeCreate(BaseModel):
    name: str
    img: str


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str


class EmployeeDetailResponse(EmployeeResponse):
    employee_logs: list[EmployeeLog] = Field(
        default_factory=list
    )