from fastapi import APIRouter, Depends, HTTPException, status
#from services.services import func1, func2, ...
from schemas.schemas import employee_response, employee_log_response, employee_create_request
from db.database import get_session
from sqlalchemy.orm import Session
from pydantic import uuid4
import services.services

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/employee", response_model=list[employee_response])
def get_employees(db : Session = Depends(get_session)):
    return services.get_employees(db)

@router.post("/employee/{picture}", response_model=employee_create_request)
def create_employee(picture : Base64Bytes, db : Session = Depends(get_session))
    if picture.decode() == b"":
        raise HTTPException(status_code=422, detail="Request contains no picture.")
    return services.create_employee(picture, db)

@router.delete("/employee/{emp_id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_employee(emp_id : uuid4, db: Session = Depends(get_session)):
    emp = db.get(Employee, emp_id)
    if emp is None: 
        raise HTTPException(status_code=404, detail="Employee not found.")
    return services.delete_employee(emp_id, db)


'''
Routes som behövs
 - get(/employees) hämtar alla uppgifter förutom bild
 - post(/employees)
 - delete(/employee)

'''