from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import FiniteFloat
from demo.schemas.comparison_schema import NearestNeighbour, ComparisonResponse
from demo.services.employee_log_services import create_employee_log
import os
import secrets
from demo.models.employee_test import EmployeeTest

def validate_api_key(api_key: str | None) -> None:
    expected_key = os.environ["DEVICE_API_KEY"]
    if api_key is None or not secrets.compare_digest(
        api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


def find_nearest_neighbour(session: Session, vector: list[FiniteFloat]) -> NearestNeighbour | None:

    distance = EmployeeTest.embedding.cosine_distance(vector)
    nearest_neighbour = session.execute(
        select(
            EmployeeTest.uuid, 
            EmployeeTest.name,
            distance.label("distance")
        ).order_by(distance).limit(1)
    ).first()

    if nearest_neighbour is not None:
        uuid, name, dist = nearest_neighbour
        similarity = 1 - dist

        return NearestNeighbour(
            uuid=uuid,
            name=name,
            similarity=similarity
        )
    
    #employee table is empty.
    return None

OPENCV_REC_THRESHHOLD = 0.363


def get_compare_response(session: Session, nearest_neighbour : NearestNeighbour | None) -> ComparisonResponse:
    if nearest_neighbour is None: #employee table is empty.
        return ComparisonResponse(
            approved=False
        )

    approved = nearest_neighbour.similarity >= OPENCV_REC_THRESHHOLD
    if approved:
        employee = session.get(EmployeeTest, nearest_neighbour.uuid)
        #a log is created in relation to the employee who got granted access.
        log = create_employee_log(session, employee, approved)

    return ComparisonResponse(
        approved=approved,
        employee_uuid=nearest_neighbour.uuid if approved else None,
        name=nearest_neighbour.name if approved else None
    )



    
