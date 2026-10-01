from datetime import datetime, timezone
from uuid import UUID

from pydantic import UUID4
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from db.database import Base
from models.employee import Employee


class EmployeeLog(Base):
    __tablename__ = "employee_log"

    uuid: Mapped[UUID] = mapped_column(UUID4, foreign_key=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

