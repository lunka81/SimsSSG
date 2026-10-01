from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from pgvector import Vector
from pydantic import UUID4
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.employee_log import EmployeeLog


# Code below omitted 👇

class Employee(Base):
    __tablename__ = "employees"

    uuid: Mapped[UUID] = mapped_column(UUID4, primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=False)
    employee_logs: Mapped[list[EmployeeLog]] = relationship(
        back_populates="nearest_image",
        passive_deletes=True)
