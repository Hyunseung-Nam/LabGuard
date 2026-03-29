from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, func, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Measurement(Base):
    """
    역할: 장비 시계열 측정값 모델.
    책임 범위: Raw/필터링 값 저장. TimescaleDB Hypertable 대상.
    외부 의존성: SQLAlchemy ORM.

    Note: TimescaleDB Hypertable은 파티셔닝 컬럼(time)이
          PK에 포함되어야 하므로 (time, device_id, metric)을 복합 PK로 사용.
    """

    __tablename__ = "measurements"
    __table_args__ = (
        PrimaryKeyConstraint("time", "device_id", "metric"),
    )

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), nullable=False)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)   # temperature, pressure, voltage
    raw_value: Mapped[float | None] = mapped_column(Float)
    filtered_value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(20))
