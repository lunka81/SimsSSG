import enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_log import EmployeeLog
    from demo.models.employee import Employee

class Admin(Base):
    __tablename__ = "admin"
    
    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("employees.uuid", ondelete="CASCADE"),
        primary_key=True
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

    #__mapper_args__ = {"polymorphic_identity": "admin"}

    employee: Mapped["Employee"] = relationship(back_populates="admin")
    #relation to employee. admin should maybe be a weak entity type (can't exist unless "owned" by an employee entity.)