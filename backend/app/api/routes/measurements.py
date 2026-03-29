import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementCreate, MeasurementResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("", response_model=list[MeasurementResponse])
async def list_measurements(
    device_id: str = Query(..., description="장비 UUID"),
    metric: str | None = Query(None),
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    limit: int = Query(200, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    목적: 특정 장비의 측정값 목록을 시간 범위로 조회합니다.
    Args:
        device_id: 장비 UUID.
        metric: 측정 항목 필터 (옵션).
        from_time: 조회 시작 시각 (옵션).
        to_time: 조회 종료 시각 (옵션).
        limit: 최대 반환 건수 (기본 200, 최대 1000).
    Returns: List[MeasurementResponse]
    Raises: 500 - DB 오류.
    """
    try:
        query = select(Measurement).where(Measurement.device_id == device_id)
        if metric:
            query = query.where(Measurement.metric == metric)
        if from_time:
            query = query.where(Measurement.time >= from_time)
        if to_time:
            query = query.where(Measurement.time <= to_time)
        query = query.order_by(Measurement.time.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.error("측정값 조회 실패: device_id=%s, %s", device_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="측정값을 불러오지 못했습니다.")


@router.post("", response_model=MeasurementResponse, status_code=201)
async def create_measurement(payload: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    """
    목적: Edge Agent가 수집한 측정값을 저장합니다.
    Args: payload (MeasurementCreate) - 측정값 데이터.
    Returns: MeasurementResponse - 저장된 측정값.
    Raises: 500 - DB 오류.
    """
    try:
        measurement = Measurement(**payload.model_dump())
        db.add(measurement)
        await db.commit()
        await db.refresh(measurement)
        return measurement
    except Exception as e:
        await db.rollback()
        logger.error("측정값 저장 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="측정값 저장에 실패했습니다.")
