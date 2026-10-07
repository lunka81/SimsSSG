from sqlalchemy.orm import Session
from sqlalchemy import select

from uuid import UUID

from demo.models.employee_test import EmployeeTest
from demo.models.employee_test_log import EmployeeTestLog
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeDetailResponse, EmployeeLogResponse
from demo.services.img_services import decode_image_to_bgr, get_embedding


def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:
    img_bytes, bgr = decode_image_to_bgr(employee_create.img)
    embedding = get_embedding(bgr)

    employee = EmployeeTest(
        embedding=embedding,
        image=img_bytes,
        name=employee_create.name,
        permission=employee_create.permission,
        description=employee_create.description,
    )

    session.add(employee)
    session.commit()
    session.refresh(employee)
    employee_response = EmployeeResponse.model_validate(employee)
    return employee_response

def create_employee_log(session: Session, employee : EmployeeTest, access_granted: bool) -> EmployeeLogResponse:
    log = EmployeeTestLog(approved = access_granted)
    employee.employee_logs.append(log)
    session.commit()
    session.refresh(log)
    return EmployeeLogResponse.model_validate(log)

def get_employees(session: Session) -> list[EmployeeResponse]:
    employees = session.scalars(select(EmployeeTest).order_by(EmployeeTest.name)).all()
    return employees

def get_employee_details(session: Session, emp_id: UUID) -> EmployeeDetailResponse:
    emp = session.get(EmployeeTest, emp_id)
    return emp
