from schemas.schemas import employee_response, employee_log_response, employee_create_request
from sqlalchemy.orm import Session
from pydantic import uuid4


def get_employees(session : Session) -> list[employee_response]:
    pass


def create_employee(picture : Base64Bytes, session : Session ) -> employee_response:
    embedding = get_embedding(Base64Bytes)

def delete_employee(id : uuid4, session : Session) ->
    