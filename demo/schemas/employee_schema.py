'''from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from demo.models.employee import Permission
from demo.models.employee_log import EmployeeLog
from demo.schemas.employee_log_schema import EmployeeLogResponse
from datetime import datetime
from pydantic import field_validator
from typing import Literal
import base64

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
    description: str | None = None

class EmployeeDetailResponse(EmployeeResponse):
    employee_logs: list[EmployeeLogResponse] = Field(
        default_factory=list
    )

class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    img: str | None = Field(default=None, min_length=1)
    permission: Literal["Standard", "Admin", "Limited"] | None = None
    description: str | None = None


class EmployeeUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    permission: Permission
    description: str | None
    img: str = Field(validation_alias="image")

    @field_validator("img", mode="before")
    @classmethod
    def image_to_string(cls, value):
        if isinstance(value, bytes):
            return base64.b64encode(value).decode("ascii")
        return value
'''

import base64
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from demo.models.employee import Permission
from demo.models.employee_log import EmployeeLog
from demo.schemas.employee_log_schema import EmployeeLogResponse
from datetime import datetime

class EmployeeCreate(BaseModel):
    name: str
    permission: Permission
    description: str | None = None
    # The image is sent as a data URL: "data:image/jpeg;base64,..."
    img: str

class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    img: str | None = Field(default=None, min_length=1)
    permission: Literal["Standard", "Admin", "Limited"] | None = None
    description: str | None = None

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    permission: Permission
    description: str | None
    img: str = Field(validation_alias="image")

    @field_validator("img", mode="before")
    @classmethod
    def image_to_string(cls, value):
        if isinstance(value, bytes):
            return base64.b64encode(value).decode("ascii")
        return value

'''
class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID 
    name: str
    permission: Permission
    description: str | None = None
'''
class EmployeeDetailResponse(EmployeeResponse):
    employee_logs: list[EmployeeLogResponse] = Field(
        default_factory=list
    )

class EmployeeUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    permission: Permission
    description: str | None