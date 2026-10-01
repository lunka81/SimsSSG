from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from pgvector.sqlalchemy import Vector
from pydantic import UUID4
from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.employee_log import EmployeeLog


# Code below omitted 👇

class Employee(Base):
    __tablename__ = "employees"

    uuid: Mapped[UUID] = mapped_column(UUID4, primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(128), nullable=False)
    image: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    employee_logs: Mapped[list["EmployeeLog"]] = relationship(
        back_populates="employee",
        passive_deletes=True
    )


