from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from sqlalchemy.orm import Session

from demo.db.database import get_session
from demo.models.employee_test import EmployeeTest
from demo.schemas.employee_schema import EmployeeResponse, EmployeeCreate, EmployeeUpdate, EmployeeUpdateResponse
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

@employee_router.patch("/{employee_uuid}",response_model=EmployeeUpdateResponse)
def update_employee(employee_uuid: UUID,employee_update: EmployeeUpdate,session: Session = Depends(get_session)):
    return employee_services.update_employee(session,employee_uuid,employee_update)

@employee_router.get("/getall",response_model=list[EmployeeResponse])
def get_all_employee(session: Session = Depends(get_session)):
    return employee_services.get_all_employee(session)