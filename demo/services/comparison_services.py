from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import FiniteFloat
from demo.schemas.comparison_schema import NearestNeighbour, ComparisonResponse, ComparisonRequest

from demo.services.employee_log_services import create_employee_log
import os
import secrets
from demo.models.employee import Employee

def validate_api_key(api_key: str | None) -> None:
    expected_key = os.environ["DEVICE_API_KEY"]
    if api_key is None or not secrets.compare_digest(
        api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

OPENCV_REC_THRESHHOLD = 0.363

#function written by anders.
#committed by me because we want to keep this branch as the most updated one.
#we have used git inefficiently in this project, which we will mention in the final report.
#generates a pseudo-accurate confidence score based on the cosine similarity when comparing an embedding with the database.
def similarity_to_match_score(
    similarity: float,
    threshold: float = OPENCV_REC_THRESHHOLD,
) -> float:
    similarity = max(0.0, min(1.0, float(similarity)))

    if similarity >= threshold:
        score = 50.0 + (
            (similarity - threshold) / (1.0 - threshold)
        ) * 50.0
    else:
        score = (similarity / threshold) * 50.0

    return round(score, 2)

def find_nearest_neighbour(session: Session, vector: list[FiniteFloat]) -> NearestNeighbour | None:

    distance = Employee.embedding.cosine_distance(vector)
    nearest_neighbour = session.execute(
        select(
            Employee.uuid,
            Employee.name,
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


def get_compare_response(
        session: Session, 
        nearest_neighbour : NearestNeighbour | None, #None if employees-table is empty.
        match_score: float | None,
        payload: ComparisonRequest
) -> ComparisonResponse:
    if nearest_neighbour is None: #employee table is empty.
        return ComparisonResponse(
            approved=False
        )

    approved = nearest_neighbour.similarity >= OPENCV_REC_THRESHHOLD
    if approved:
        employee = session.get(Employee, nearest_neighbour.uuid)
        #a log is created in relation to the employee who got granted access.
        log = create_employee_log(
            session, 
            employee, 
            match_score,
            payload.camera_id,
            payload.detection_confidence,
            payload.face_width,
            payload.face_height
        )

    return ComparisonResponse(
        approved=approved,
        employee_uuid=nearest_neighbour.uuid if approved else None,
        name=nearest_neighbour.name if approved else None
    )



    
