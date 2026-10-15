from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field



class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1)
    img: str = Field(min_length=1)
    role: Literal["Standard", "Admin", "Limited"]
    description: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    img: str | None = Field(default=None, min_length=1)
    role: Literal["Standard", "Admin", "Limited"] | None = None
    description: str | None = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: UUID
    name: str
    role: Literal["Standard", "Admin", "Limited"] | None = None
    description: str | None = None


class EmployeeUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: UUID
    name: str
