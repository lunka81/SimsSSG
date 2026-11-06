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

@log_router.get(
    "/",
    response_model = list[EmployeeLogResponse],
    summary="HTTP GET endpoint for getting a given number of logs created before a given timestamp.",
    description="Number of logs defaults to 30, and can be between [1, 100]."    
)
def get_logs_before_timestamp(
    limit: int = Query(30, ge=1, le=100), #frontend decides n logs to fetch
    before: datetime | None = None, #return n logs before this timestamp
    session: Session = Depends(get_session)
):
    return employee_log_services.get_logs_before_timestamp(limit, before, session)