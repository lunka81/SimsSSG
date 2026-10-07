from fastapi import APIRouter, Depends, HTTPException, Response, status

from deepface.modules.exceptions import FaceNotDetected
from sqlalchemy.orm import Session
from uuid import UUID
from demo.db.database import get_session
from demo.schemas.employee_schema import (
    EmployeeResponse, 
    EmployeeDetailResponse, 
    EmployeeLogResponse, 
    EmployeeCreate,
)
                                          
from demo.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from demo.services import employee_services

from demo.models.employee_test import EmployeeTest
from demo.services.img_services import image_media_type

employee_router = APIRouter(
    prefix="/api/employee",
    tags=["employee"]
)

@employee_router.get("/", response_model=list[EmployeeResponse])
def get_employees(session: Session = Depends(get_session)):
    return employee_services.get_employees(session)

@employee_router.get("/{emp_id}", response_model=EmployeeDetailResponse)
def get_employee(emp_id: UUID, session: Session = Depends(get_session)):
    emp = employee_services.get_employee_details(session, emp_id)
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")
    return emp

#the image is sent as a regular image file so that it can be used directly in <img src="...">
@employee_router.get("/{emp_id}/image")
def get_employee_image(emp_id: UUID, session: Session = Depends(get_session)):
    emp = employee_services.get_employee_details(session, emp_id)
    if emp is None: #if id isn't found cached or in db  
        raise HTTPException(status_code=404, detail="Employee not found.")
    return Response(content=emp.image, media_type=image_media_type(emp.image))

#store
@employee_router.post("/",response_model=EmployeeResponse, status_code=201)
def add_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    try:
        return employee_services.add_employee(session, employee)
    except FaceNotDetected: #DeepFace found no face in the image
        raise HTTPException(status_code=422, detail="No face found in the picture.")

@employee_router.post("/employee_log/{emp_id}", response_model=EmployeeLogResponse)
def create_employee_log(emp_id: UUID, approved: bool, session: Session = Depends(get_session)):
    emp = session.get(EmployeeTest, emp_id)
    if emp is None: #if id isn't found cached or in db
            raise HTTPException(status_code=404, detail="Employee not found.")
    return employee_services.create_employee_log(session, emp, approved)

@employee_router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: UUID, session: Session = Depends(get_session)):
    emp = session.get(EmployeeTest, emp_id)
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")
    session.delete(emp)
    session.commit()