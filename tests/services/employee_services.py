from sqlalchemy.orm import Session

from tests.models import employee_test
from tests.models.employee_test import Employee
from tests.schemas.employee_schema import EmployeeCreate, EmployeeResponse


def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:
    employee = Employee(**employee_create.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    employee_response = EmployeeResponse.model_validate(employee)
    return employee_response

