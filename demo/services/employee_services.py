from sqlalchemy.orm import Session
from torch.nn.functional import embedding

from demo.models import employee_test
from demo.models.employee_test import EmployeeTest
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from demo.services.img_services import decode_image_to_bgr


def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:

    img_bytes, bgr = decode_image_to_bgr(employee_create.image)


    employee = EmployeeTest(**employee_create.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    employee_response = EmployeeResponse.model_validate(employee)
    return employee_response

