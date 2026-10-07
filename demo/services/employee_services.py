import binascii

from fastapi import HTTPException
from PIL import UnidentifiedImageError
from sqlalchemy.orm import Session

from demo.models.employee_test import EmployeeTest
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from demo.services.face_embedding_service import (
    get_face_embedding_service,
)
from demo.services.img_services import decode_image_to_bgr


def add_employee(
    session: Session,
    employee_create: EmployeeCreate,
) -> EmployeeResponse:
    name = employee_create.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Namn måste anges.",
        )

    try:
        img_bytes, bgr = decode_image_to_bgr(employee_create.img)
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

    face_service = get_face_embedding_service()

    try:
        face_embedding = face_service.create_embedding(bgr)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    employee = EmployeeTest(
        name=name,
        role=employee_create.role,
        description=employee_create.description,
        image=img_bytes,
        embedding=face_embedding,
    )

    try:
        session.add(employee)
        session.commit()
        session.refresh(employee)
    except Exception:
        session.rollback()
        raise

    return EmployeeResponse.model_validate(employee)