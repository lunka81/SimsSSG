from pydantic import BaseModel
from uuid import UUID
from demo.schemas.employee_schema import EmployeeCreate
class AdminCreate(EmployeeCreate):
    username: str
    plain_password: str 

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    username: str
    uuid: UUID

class AdminLoginResponse(AdminResponse):
    access_token: str #str?
