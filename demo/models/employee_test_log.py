from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from demo.db.database import Base

if TYPE_CHECKING:
    from demo.models.employee_test import EmployeeTest


class EmployeeTestLog(Base):
    __tablename__ = "employee_log"

    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    employee_uuid: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("employees.uuid"),
        nullable=True,
        index=True
    )

    approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    employee: Mapped["EmployeeTest | None"] = relationship(
        back_populates="employee_logs"
    )