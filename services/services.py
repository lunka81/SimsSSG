from schemas.schemas import employee_response, employee_log_response, employee_create_request
from sqlalchemy.orm import Session


def get_employees(session : Session) -> list[employee_response]:
    