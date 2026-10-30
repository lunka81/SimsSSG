from sqlalchemy.orm import Session
from sqlalchemy import select
from demo.models.employee_log import EmployeeLog
from demo.models.employee import Employee
from demo.schemas.employee_log_schema import EmployeeLogResponse
from datetime import datetime
from pydantic import FiniteFloat

def create_employee_log(
    session: Session, 
    employee: Employee,
    match_score: float,
    camera_id: str,
    detection_confidence: FiniteFloat,
    face_width: int,
    face_height: int
) -> EmployeeLogResponse:

    log = EmployeeLog(
        match_score = match_score,
        camera_id = camera_id,
        detection_confidence = detection_confidence,
        face_width = face_width,
        face_height = face_height
    )
    employee.employee_logs.append(log)
    
    session.commit()
    session.refresh(log)
    return EmployeeLogResponse.model_validate(log)

"""
Function that returns {limit} no. of employee logs created
before a given timestamp. A manual form of pagination 
for the employee logs page in the web app.  
"""
def get_logs_before_timestamp(
        limit: int, 
        before: datetime | None, 
        session: Session
) -> list[EmployeeLogResponse]:
    query = (select(EmployeeLog)
        .order_by(EmployeeLog
                  .timestamp.desc())
        .limit(limit)
    )
    if before is not None:
        query = query.where(EmployeeLog.timestamp < before)
    return session.scalars(query).all()
