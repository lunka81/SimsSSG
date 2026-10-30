from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from demo.models.employee import Employee, Permission
from demo.models.employee_log import EmployeeLog
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeDetailResponse, EmployeeUpdate, EmployeeUpdateResponse
from demo.services.img_services import decode_image_to_bgr, get_embedding

from fastapi import HTTPException
from PIL import UnidentifiedImageError
import binascii


def add_employee(session: Session, employee_create:EmployeeCreate)->EmployeeResponse:
    employee = build_employee(employee_create)
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    employee_response = EmployeeResponse.model_validate(employee)
    return employee_response

def build_employee(employee_create: EmployeeCreate) -> Employee:
    img_bytes, bgr = decode_image_to_bgr(employee_create.img)
    embedding = get_embedding(bgr)
    
    employee = Employee(
            embedding=embedding,
            image=img_bytes,
            name=employee_create.name,
            permission=employee_create.permission,
            description=employee_create.description,
        )
    return employee

def get_employees(session: Session) -> list[EmployeeResponse]:
    employees = session.scalars(select(Employee).order_by(Employee.name)).all()
    return employees

def get_employee_details(session: Session, emp_id: UUID) -> EmployeeDetailResponse:
    emp = session.get(Employee, emp_id)
    return emp

def update_employee(session: Session, employee_uuid: UUID, employee_update: EmployeeUpdate )->EmployeeUpdateResponse:
    employee = session.get(Employee, employee_uuid)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Personen hittades inte.",
        )

    changes = employee_update.model_dump(exclude_unset=True)

    for field in ("name", "permission", "img"):
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} får inte vara null.",
            )

    if "name" in changes:
        changes["name"] = changes["name"].strip()

        if not changes["name"]:
            raise HTTPException(
                status_code=422,
                detail="Namn måste anges.",
            )

        # Skapa ny embedding endast när en ny bild skickas.
    if "img" in changes:
        image_data = changes.pop("img")

        try:
            img_bytes, bgr = decode_image_to_bgr(image_data)
        except (
                ValueError,
                binascii.Error,
                UnidentifiedImageError,
                OSError,
        ) as error:
            raise HTTPException(
                status_code=422,
                detail="Bilden kunde inte avkodas.",
            ) from error



        try:
            embedding = get_embedding(bgr)
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        changes["image"] = img_bytes
        changes["embedding"] = embedding

    try:
        for field, value in changes.items():
            setattr(employee, field, value)

        session.commit()
        session.refresh(employee)
    except Exception:
        session.rollback()
        raise

    return EmployeeUpdateResponse.model_validate(employee)