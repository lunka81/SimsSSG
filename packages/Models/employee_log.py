# models/employee_log.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.employee import Employee


class EmployeeLog(Base):
    __tablename__ = "employee_logs"

    # Unikt ID för ett sökförsök.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Närmaste sparade bildrad. Kan vara NULL om inget ansikte hittades
    # eller om anti-spoofing avvisade bilden före databassökningen.
    nearest_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Exempel: "match", "no_match", "spoof_rejected", "no_face".
    result: Mapped[str] = mapped_column(String(30), nullable=False)

    # Mått från kamerabilden. Kameravståndet är en uppskattning.
    estimated_camera_distance_cm: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    face_width_ratio: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Cosine distance till närmaste bild.
    # NULL om försöket stoppades innan vektorsökningen.
    vector_distance: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    threshold: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Tider i millisekunder. Ett steg som inte kördes får NULL.
    detection_embedding_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    anti_spoofing_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    database_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Anti-spoofing kan sakna resultat om kontrollen inte kördes.
    is_real: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    # Gör testresultat jämförbara även efter ett framtida modellbyte.
    model_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    detector_backend: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    # Valfri manuell testetikett, t.ex. "anders" eller "okänd".
    # Det är facit som du anger vid ett kontrollerat test,
    # inte en identitet som modellen själv har förutsagt.
    expected_label: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    nearest_image: Mapped[Employee | None] = relationship(
        back_populates="recognition_logs"
    )