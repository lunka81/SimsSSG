import binascii

from fastapi import HTTPException, Depends
from PIL import UnidentifiedImageError
from sqlalchemy.orm import Session

from demo.models.employee_test import EmployeeTest
from demo.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdateResponse, EmployeeUpdate
from demo.services.face_embedding_service import (
    get_face_embedding_service,
)
from demo.services.img_services import decode_image_to_bgr

from uuid import UUID




from sqlalchemy import select


def get_all_employee(session: Session) -> list[EmployeeTest]:
    return list(session.scalars(select(EmployeeTest)).all())


def update_employee(session: Session,employee_uuid: UUID,employee_update: EmployeeUpdate) -> EmployeeUpdateResponse:

    employee = session.get(EmployeeTest, employee_uuid)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Personen hittades inte.",
        )

    changes = employee_update.model_dump(exclude_unset=True)

    # Dessa databasfält får inte vara null.
    for field in ("name", "role", "img"):
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

        face_service = get_face_embedding_service()

        try:
            face_embedding = face_service.create_embedding(bgr)
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        changes["image"] = img_bytes
        changes["embedding"] = face_embedding

    try:
        for field, value in changes.items():
            setattr(employee, field, value)

        session.commit()
        session.refresh(employee)
    except Exception:
        session.rollback()
        raise

    return EmployeeUpdateResponse.model_validate(employee)




def add_employee(session: Session,employee_create: EmployeeCreate) -> EmployeeResponse:

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