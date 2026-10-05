from schemas.schemas import employee_response, employee_log_response, employee_create_request
from models.employee import Employee
from models.employee_log import EmployeeLog
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import Base64Bytes
#from pgvector.sqlalchemy import Vector 
from deepface import DeepFace
import numpy as np
import cv2


def get_embedding(picture : Base64Bytes) -> list[float]:
    #recognition flow: picture > get_embedding() > find closest Employee by embedding > create_employee_log(employee, session)

    #128 dimensions
    pass

def get_employees(session : Session) -> list[employee_response]:
    employees = session.query(Employee).all()
    return employees

def create_employee(picture : Base64Bytes, session : Session) -> employee_response:
    embedding = get_embedding(picture)

def create_employee_log(employee : Employee, session : Session) -> employee_log_response:
    log = EmployeeLog()
    employee.employee_logs.append(log)
    session.commit()
    session.refresh(log)
    #return ORM object works because the response model can read ORM attributes
    return log

def delete_employee(employee : Employee, session : Session):
    session.delete(employee)W
    session.commit()    
    