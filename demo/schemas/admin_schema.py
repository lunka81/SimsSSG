from pydantic import BaseModel
from uuid import UUID
from demo.schemas.employee_schema import EmployeeCreate
class AdminCreate(EmployeeCreate):
    username: str
    hash_password: str #ändra detta till hash-typen

class AdminResponse(BaseModel):
    username: str
    uuid: UUID

class AdminLoginResponse(AdminResponse):
    approved: bool
