from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import LargeBinary, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_test_log import EmployeeTestLog


class EmployeeTest(Base):
    __tablename__ = "employees"

    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    embedding: Mapped[list[float]] = mapped_column(
        VECTOR(128),
        nullable=False
    )

    image: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    employee_logs: Mapped[list["EmployeeTestLog"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )