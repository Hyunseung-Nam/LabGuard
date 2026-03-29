import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Device(Base):
    """
    역할: 실험 장비 메타데이터 모델.
    책임 범위: 장비 식별 정보, 통신 설정, 임계치 보관.
    외부 의존성: SQLAlchemy ORM.
    """

    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    protocol: Mapped[str] = mapped_column(String(50), nullable=False)  # serial, tcp, visa, modbus
    config: Mapped[dict | None] = mapped_column(JSON)                   # 프로토콜별 연결 설정
    threshold: Mapped[dict | None] = mapped_column(JSON)                # 임계치 설정
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
