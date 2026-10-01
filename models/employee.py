from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

if TYPE_CHECKING:
    from models.employee_log import EmployeeLog


class Employee(Base):
    __tablename__ = "employees"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    embedding: Mapped[list[float]] = mapped_column(Vector(128), nullable=False)

    # One employee -> many log entries. Deleting an employee lets the database
    # cascade-delete their logs (see ondelete="CASCADE" on the foreign key).
    employee_logs: Mapped[list["EmployeeLog"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
