from fastapi import APIRouter, Depends, HTTPException, Response, status, Header
from demo.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from demo.services import comparison_services
from sqlalchemy.orm import Session
from demo.db.database import get_session
recognition_router = APIRouter(
    prefix="/recognition",
    tags=["identify"]
)

#compare
#an employee log is created here if a match is made.
@recognition_router.post("/identify", response_model = ComparisonResponse, status_code = 200)
def compare_employee(
    payload : ComparisonRequest, 
    session: Session = Depends(get_session),
    x_api_key: str | None = Header(default=None)
): #the parameter name decides which header FastAPI reads. (important)

    comparison_services.validate_api_key(x_api_key)

    '''
    flow:
    validate api key -> find nearest face in db -> construct result -> http response to Pi

    response should contain:
        - Approved
        - UUID (opt)
        - Name (opt)

    response function should receive:
        - Recognition confidence
        - Closest match (EmployeeTest)
    '''
    nearest_neighbour=comparison_services.find_nearest_neighbour(session, payload.embedding)
    response=comparison_services.get_compare_response(session, nearest_neighbour)
    return response