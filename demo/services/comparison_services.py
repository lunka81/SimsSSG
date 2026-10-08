from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import FiniteFloat
from demo.schemas.comparison_schema import ComparisonDetailResponse, ComparisonResponse, NearestNeighbourResponse
from demo.services.employee_log_services import create_employee_log
import os
import secrets
from demo.models.employee_test import EmployeeTest

def validate_api_key(api_key: str) -> bool:
    expected_key = os.environ["DEVICE_API_KEY"]
    if api_key is None or not secrets.compare_digest(
        api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

def find_nearest_employee(session: Session, embedding: list[FiniteFloat]) -> NearestNeighbourResponse:
    """
        TODO:
            Test implementera detta med pgvector's inbyggda 
            nearest neighbour-funktioner.
    """
    pass

def get_compare_response(session: Session, nearest_neighbour : NearestNeighbourResponse) -> ComparisonResponse:
    #placeholder threshhold
    CONFIDENCE_THRESHHOLD = 0.80
    if nearest_neighbour.confidence >= CONFIDENCE_THRESHHOLD:

        
        
        """
            Changed the NearestNeighbour Schema, 
            neighbour.employee.x doesn't work anymore
        """
        employee = session.get(EmployeeTest, nearest_neighbour.employee.uuid)
        
        #sufficient confidence in employee match -> employee gets a new log.
        
        #TODO: Invalid call
        create_employee_log(employee, session) 
        return ComparisonResponse(
            approved=True,
            employee_uuid=nearest_neighbour.employee.uuid,
            name=nearest_neighbour.employee.name
        )

    #confidence not high enough -> comparison isn't tied to nearest employee.
    return ComparisonResponse(
        approved=False,
        employee_uuid=None,
        name=None
    )

    
