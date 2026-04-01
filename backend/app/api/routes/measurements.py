import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.measurement import Measurement
from app.models.device import Device
from app.models.alert import AlertEvent
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.core.config import settings
from app.services.telegram import send_alert

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/measurements", tags=["measurements"])


async def _check_threshold_and_alert(
    db: AsyncSession,
    device: Device,
    metric: str,
    value: float,
    unit: str | None,
    measured_at: datetime,
) -> None:
    """
    목적: 측정값이 장비 임계치를 초과하면 AlertEvent를 생성하고 Telegram 알림을 발송합니다.
    Args:
        db: DB 세션.
        device: 장비 모델 인스턴스.
        metric: 측정 항목명 (temperature, pressure 등).
        value: 측정값.
        unit: 단위 문자열 (°C, hPa 등).
        measured_at: 측정 시각 (쿨다운 기준).
    Returns: 없음.
    Side Effects: 임계치 초과 시 AlertEvent를 DB에 추가하고 Telegram 메시지를 발송합니다.
    Raises: 없음 (오류는 로그 처리).
    """
    threshold = (device.threshold or {}).get(metric)
    if not threshold:
        return

    min_val = threshold.get("min")
    max_val = threshold.get("max")
    exceeded_threshold = None
    is_upper = False

    if max_val is not None and value > max_val:
        exceeded_threshold = max_val
        is_upper = True
    elif min_val is not None and value < min_val:
        exceeded_threshold = min_val
        is_upper = False

    if exceeded_threshold is None:
        return

    unit_str = f" {unit}" if unit else ""
    direction = f"상한 {exceeded_threshold} 초과" if is_upper else f"하한 {exceeded_threshold} 미달"
    db_message = f"[{device.name}] {metric} {value:.3f}{unit_str} → {direction}"

    # 쿨다운: 동일 장비+측정항목 알림이 최근 N초 내 있으면 생성 안 함
    cooldown_since = measured_at - timedelta(seconds=settings.ALERT_COOLDOWN_SECONDS)
    result = await db.execute(
        select(AlertEvent)
        .where(AlertEvent.device_id == device.id)
        .where(AlertEvent.metric == metric)
        .where(AlertEvent.time >= cooldown_since)
        .limit(1)
    )
    if result.scalar_one_or_none():
        logger.debug("알림 쿨다운 중: device_id=%s, metric=%s", device.id, metric)
        return

    db.add(AlertEvent(
        device_id=device.id,
        severity="ALERT",
        metric=metric,
        value=value,
        threshold=exceeded_threshold,
        message=db_message,
    ))
    logger.warning("이상값 감지 → 알림 생성: %s", db_message)

    # 심각도별 이모지: 상한 초과 🔴 / 하한 미달 🔵
    emoji = "🔴" if is_upper else "🔵"
    time_str = measured_at.strftime("%H:%M:%S")
    location = f"{device.location} · " if device.location else ""
    telegram_message = (
        f"{emoji} <b>{device.name}</b>\n"
        f"{metric} {value:.3f}{unit_str} → {direction}\n"
        f"{location}{time_str}"
    )
    await send_alert(telegram_message)


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

        # 이상값 감지: 장비 임계치와 비교 후 필요 시 AlertEvent 생성
        if payload.raw_value is not None:
            device = await db.get(Device, payload.device_id)
            if device:
                await _check_threshold_and_alert(
                    db, device, payload.metric, payload.raw_value,
                    payload.unit, measurement.time or datetime.now(),
                )

        await db.commit()
        await db.refresh(measurement)
        return measurement
    except Exception as e:
        await db.rollback()
        logger.error("측정값 저장 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="측정값 저장에 실패했습니다.")
