from fastapi import APIRouter, Depends, Query
from datetime import datetime
from sqlalchemy.orm import Session
from demo.db.database import get_session
from demo.schemas.employee_log_schema import EmployeeLogResponse

from demo.services.auth_services import verify_access_token
                                        
from demo.services import employee_log_services

log_router = APIRouter(
    prefix="/api/employee_logs",
    dependencies=[Depends(verify_access_token)]
)

@log_router.get("/", response_model = list[EmployeeLogResponse])
def get_last_n_logs(
    limit: int = Query(30, ge=1, le=100),
    before: datetime | None = None,
    session: Session = Depends(get_session)
):
    return employee_log_services.get_logs_before_timestamp(limit, before, session)