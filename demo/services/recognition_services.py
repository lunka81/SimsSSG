import math
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from demo.models.employee_test import EmployeeTest


def identify_employee(
    session: Session,
    embedding: list[float],
) -> dict:
    threshold = float(os.environ["FACE_SIMILARITY_THRESHOLD"])

    if not math.isfinite(threshold) or not -1 <= threshold <= 1:
        raise RuntimeError("Ogiltig FACE_SIMILARITY_THRESHOLD.")

    distance = EmployeeTest.embedding.cosine_distance(embedding)

    # Hämta bara identitet och avstånd, inte bildbytes.
    statement = (
        select(
            EmployeeTest.uuid,
            EmployeeTest.name,
            distance.label("distance"),
        )
        .order_by(distance)
        .limit(1)
    )

    match = session.execute(statement).first()

    if match is None:
        return {
            "approved": False,
            "employee_uuid": None,
            "name": None,
            "similarity": None,
            "reason": "no_registered_employees",
        }

    # Cosine similarity = 1 - cosine distance.
    similarity = 1.0 - float(match.distance)

    if not math.isfinite(similarity):
        return {
            "approved": False,
            "employee_uuid": None,
            "name": None,
            "similarity": None,
            "reason": "invalid_comparison",
        }

    approved = similarity >= threshold

    print(
        f"Cosine similarity: {similarity:.4f}, "
        f"threshold: {threshold:.4f}, "
        f"approved: {approved}"
    )

    return {
        "approved": approved,
        "employee_uuid": match.uuid if approved else None,
        "name": match.name if approved else None,
        "similarity": similarity,
        "reason": "face_match" if approved else "no_match",
    }