from fastapi import APIRouter, Depends, HTTPException, Response, status, Header
from demo.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from demo.services import comparison_services
from sqlalchemy.orm import Session
from demo.db.database import get_session
recognition_router = APIRouter(
    prefix="/recognition/identify",
    tags=["identify"]
)

#compare
#an employee log is created here if a match is made.
@recognition_router.post("/", response_model = ComparisonResponse)
def compare_employee(payload : ComparisonRequest, session: Session = Depends(get_session)):
    api_key : str | None = Header(default = None)
    comparison_services.validate_api_key(api_key)
    
    nearest_emp=comparison_services.find_nearest_employee(session, payload.embedding)
    response=comparison_services.get_compare_response(nearest_emp)
    
    return response