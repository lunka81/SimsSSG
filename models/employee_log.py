'''from db.database import Base
from models.employee import Employee
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeeLog(Base):
    __tablename__ = "employee_log"

    timestamp: Mapped[datetime] = mapped_column(
        datetime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )'''
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import UUID4
from sqlalchemy import DateTime, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from db.database import Base
from models.employee import Employee

if TYPE_CHECKING:
    from models.employee import Employee

class EmployeeLog(Base):
    __tablename__ = "employee_log"

    uuid: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    employee_uuid: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("employee.uuid"),
        nullable=False,
        index=True
    )
    
    employee: Mapped[list["Employee"]] = relationship(
        back_populates="employee_logs"

    )