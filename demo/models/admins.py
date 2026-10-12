import enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Enum, LargeBinary, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_test_log import EmployeeTestLog

class EmployeeTest(Base):
    __tablename__ = "admin"

    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
