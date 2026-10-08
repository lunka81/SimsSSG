from sqlalchemy.orm import Session
from demo.models.employee_test_log import EmployeeTestLog
from demo.models.employee_test import EmployeeTest
from demo.schemas.employee_log_schema import EmployeeLogResponse

def create_employee_log(session: Session, employee : EmployeeTest, access_granted: bool) -> EmployeeLogResponse:
    log = EmployeeTestLog(approved = access_granted)
    employee.employee_logs.append(log)
    session.commit()
    session.refresh(log)
    return EmployeeLogResponse.model_validate(log)
