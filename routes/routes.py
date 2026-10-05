from fastapi import APIRouter, Depends, HTTPException, status
#from services.services import func1, func2, ...
from schemas.schemas import employee_response, employee_log_response, employee_create_request
from db.database import get_session
from sqlalchemy.orm import Session
from uuid import UUID
from services import services
from models.employee import Employee
from pydantic import Base64Bytes

router = APIRouter(prefix="/routes", tags=["routes"])

@router.get("/employee", response_model=list[employee_response])
def get_employees(db : Session = Depends(get_session)):
    return services.get_employees(db)

@router.post("/employee", response_model=employee_response)
def create_employee(payload : employee_create_request, db : Session = Depends(get_session)):
    if not payload.picture:
        raise HTTPException(status_code=422, detail="Request contains no picture.")
    return services.create_employee(payload.picture, db)

@router.post("employee_log/{emp_id}", response_model = employee_log_response)
def create_log(emp_id : UUID, session : Session = Depends(get_session)):
    #this endpoint should never be reached unless a face can be tied to an id, so i don't think a check is necessary.
    return services.create_employee_log(emp_id,)

@router.delete("/employee/{emp_id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_employee(emp_id : UUID, session: Session = Depends(get_session)):
    emp = session.get(Employee, emp_id)
    if emp is None: 
        raise HTTPException(status_code=404, detail="Employee not found.")
    services.delete_employee(emp, session)



'''
Routes som behövs
 - get(/employees) hämtar alla uppgifter förutom bild
 - post(/employees)
 - delete(/employee)

'''