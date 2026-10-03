from schemas.schemas import employee_response, employee_log_response, employee_create_request
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import Base64Bytes
from pgvector.sqlalchemy import Vector 
from deepface import DeepFace
import numpy as np
import cv2

from models.employee import employee

def get_embedding(picture : Base64Bytes) -> Vector:
    #128 dimensions

def get_employees(session : Session) -> list[employee_response]:
    pass

def create_employee(picture : Base64Bytes, session : Session) -> employee_response:
    embedding = get_embedding(Base64Bytes)

def delete_employee(id : uuid4, session : Session):

    