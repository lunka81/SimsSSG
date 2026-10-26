from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Uuid, String, Integer, Float
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

    employee_uuid: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("employees.uuid"),
        nullable=False, #Only approved access attempts are logged
        index=True
    )

    match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    camera_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    detection_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False 
    )

    face_width: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    face_height: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    employee: Mapped["EmployeeTest"] = relationship(
        back_populates="employee_logs"
    )