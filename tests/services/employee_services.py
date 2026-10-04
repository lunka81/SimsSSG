from sqlalchemy.orm import Session
from torch.nn.functional import embedding

from tests.models import employee_test
from tests.models.employee_test import Employee
from tests.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from tests.services.img_services import decode_image_to_bgr


def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:

    img_bytes, bgr = decode_image_to_bgr(employee_create.image)


    employee = Employee(**employee_create.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    employee_response = EmployeeResponse.model_validate(employee)
    return employee_response

