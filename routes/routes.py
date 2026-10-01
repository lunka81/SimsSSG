from fastapi import APIRouter, Depends
#from services.services import func1, func2, ...
from schemas.schemas import employee_response, employee_log_response, employee_create_request
from db.database import get_session
from sqlalchemy.orm import Session
import services.services

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/employee", response_model=employee_response)
def get_employees(db : Session = Depends(get_session)):
    return services.get_employees()

@router.post("/employee", response_model=employee_create_request)
def create_employee()


'''
Routes som behövs
 - get(/employees) hämtar alla uppgifter förutom bild
 - post(/employees)
 - delete(/employee)

'''