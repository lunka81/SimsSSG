from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy.orm import Session
from uuid import UUID
from demo.db.database import get_session
from demo.schemas.employee_schema import (
    EmployeeResponse, 
    EmployeeDetailResponse, 
    EmployeeCreate
)

from demo.services.auth_services import verify_access_token
                                        
from demo.services import employee_services

from demo.models.employee_test import EmployeeTest, Permission
from demo.services.img_services import image_media_type

#a token has to be sent with every request to these endpoints,
#in order to verify the admin's identity. 
employee_router = APIRouter(
    prefix="/api/employee",
    dependencies=[Depends(verify_access_token)]
)

@employee_router.get(
    "/",
    response_model=list[EmployeeResponse],
    summary="HTTP GET endpoint to get a list of all employees in the database.",
    description="Includes all attributes except embedding and logs."
)
def get_employees(session: Session = Depends(get_session)):
    return employee_services.get_employees(session)

@employee_router.get(
    "/{emp_id}", 
    response_model=EmployeeDetailResponse,
    summary="HTTP GET endpoint to get the data of a specified employee.",
    description="This data includes the employee's logs."
)
def get_employee(emp_id: UUID, session: Session = Depends(get_session)):
    emp = employee_services.get_employee_details(session, emp_id)
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")
    return emp

#the image is sent as a regular image file so that it can be used directly in <img src="...">
@employee_router.get(
    "/{emp_id}/image",
    summary="HTTP GET endpoint to get the database image of a specified employee.",
    description="Convenient for direct data-url use in the frontend."
)
def get_employee_image(emp_id: UUID, session: Session = Depends(get_session)):
    emp = employee_services.get_employee_details(session, emp_id)
    if emp is None: #if id isn't found cached or in db  
        raise HTTPException(status_code=404, detail="Employee not found.")
    return Response(content=emp.image, media_type=image_media_type(emp.image))

#store
@employee_router.post(
    "/",
    response_model=EmployeeResponse, 
    status_code=201,
    summary="HTTP POST endpoint for creating a new employee row.",
    description="Exceptions are handled elsewhere."
)
def add_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    return employee_services.add_employee(session, employee) #exceptions handled in img_services.py
        
@employee_router.delete(
    "/{emp_id}", 
    status_code=204,
    summary="HTTP DELETE endpoint for deleting an employee row.",
    description="Empty response body, following http conventions"
)
def delete_employee(emp_id: UUID, session: Session = Depends(get_session)):
    emp = session.get(EmployeeTest, emp_id)
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")
    session.delete(emp)
    session.commit()