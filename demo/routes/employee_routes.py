from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from demo.db.database import get_session
from demo.schemas.employee_schema import EmployeeResponse, EmployeeCreate
from demo.services import employee_services

employee_router = APIRouter(
    prefix="/api/employee",
    tags=["employee"]
)

#lagra
@employee_router.post("/",response_model=EmployeeResponse, status_code=201)
def add_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    return employee_services.add_employee(session, employee)


#jämföra
@employee_router.post("/",response_model=EmployeeResponse, status_code=201)
def compare_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    return employee_services.add_employee(session, employee)