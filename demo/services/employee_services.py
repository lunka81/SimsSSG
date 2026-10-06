from sqlalchemy.orm import Session

from demo.models import employee_test
from demo.models.employee_test import EmployeeTest
from demo.models.employee_test_log import EmployeeTestLog
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeLogResponse
from demo.services.img_services import decode_image_to_bgr

def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:
    img_bytes, bgr = decode_image_to_bgr(employee_create.img)
    embedding = get_embedding(employee_create.img)

    #employee = EmployeeTest(**employee_create.model_dump())

    employee = EmployeeTest(
        employee_create.name,
        employee_create.img, 
        embedding
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
    return EmployeeLogResponse(
        name=employee.name,
        uuid=log.uuid,
        timestamp=log.timestamp,
        approved=log.approved,
    )
