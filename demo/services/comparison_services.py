from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import FiniteFloat
from demo.schemas.comparison_schema import ComparisonDetailResponse
import os
import secrets

def validate_api_key(api_key: str) -> bool:
    expected_key = os.environ["DEVICE_API_KEY"]
    if api_key is None or not secrets.compare_digest(
        api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

def find_nearest_employee(session: Session, embedding: list[FiniteFloat]) -> ComparisonDetailResponse:
    pass