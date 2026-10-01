from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

if TYPE_CHECKING:
    from models.employee import Employee


class EmployeeLog(Base):
    __tablename__ = "employee_logs"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    employee_uuid: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("employees.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Many log entries -> one employee.
    employee: Mapped["Employee"] = relationship(back_populates="employee_logs")
