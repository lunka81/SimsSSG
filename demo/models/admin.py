import enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_test_log import EmployeeTestLog
    from demo.models.employee_test import EmployeeTest

class Admin(Base):
    __tablename__ = "admin"

    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    employee_uuid: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("employees.uuid", ondelete="CASCADE"),
        nullable=False, #admin account must be tied to an employee
        unique=True #employee can have max 1 admin account
    )

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )

    employee: Mapped["EmployeeTest"] = relationship(back_populates="admin")
    #hash_password: Mapped[something] = mapped_column()
    #relation to employee. admin should maybe be a weak entity type (can't exist unless "owned" by an employee entity.)