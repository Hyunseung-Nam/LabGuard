from datetime import datetime
from sqlalchemy import String, Float, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class AlertEvent(Base):
    """
    역할: 이상 감지 알림 이벤트 로그 모델.
    책임 범위: 알림 발생 기록 및 발송 상태 추적.
    외부 의존성: SQLAlchemy ORM.
    """

    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # WARNING, ALERT, OFFLINE
    metric: Mapped[str | None] = mapped_column(String(50))
    value: Mapped[float | None] = mapped_column(Float)
    threshold: Mapped[float | None] = mapped_column(Float)
    message: Mapped[str | None] = mapped_column(Text)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)
