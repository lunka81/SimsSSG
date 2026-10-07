import enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Enum, LargeBinary, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_test_log import EmployeeTestLog


class Permission(str, enum.Enum):
    STANDARD = "Standard"
    ADMIN = "Admin"
    LIMITED = "Limited"


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
        nullable=False,
        # The image is only loaded when it is used, not every time the list is loaded
        deferred=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    permission: Mapped[Permission] = mapped_column(
        # values_callable: store "Standard" in the database instead of "STANDARD"
        Enum(Permission, name="permission", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=Permission.STANDARD
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    employee_logs: Mapped[list["EmployeeTestLog"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )