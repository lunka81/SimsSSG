from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from uuid import UUID
from demo.db.database import get_session
from demo.schemas.employee_schema import EmployeeResponse, EmployeeLogResponse, EmployeeCreate
from demo.services import employee_services
from demo.models.employee_test import EmployeeTest

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

@employee_router.post("/employee_log/{emp_id}", response_model=EmployeeLogResponse)
def create_employee_log(emp_id: UUID, approved: bool, session: Session = Depends(get_session)):
    emp = session.get(EmployeeTest, emp_id)
    return employee_services.create_employee_log(session, emp, approved)

@employee_router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: UUID, session: Session = Depends(get_session)):
    emp = session.get(EmployeeTest, emp_id)
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")
    session.delete(emp)
    session.commit()