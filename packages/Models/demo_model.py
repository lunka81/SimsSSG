from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, JSON
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from Database.database import Base

class Employee(Base):
    __tablename__ = 'employee'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(
                String, nullable=False
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(512), nullable=False
    )
    logs: Mapped[list[str]] = mapped_column(
            JSON, nullable=False, default=list
    )
    name: Mapped[str] = mapped_column(
            String, nullable=False
    )
    timestamp : Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    approved : Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    picture : Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False
    )
    