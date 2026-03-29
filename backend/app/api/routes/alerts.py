import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.alert import AlertEvent
from app.schemas.alert import AlertResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    device_id: str | None = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    목적: 알림 이벤트 목록을 반환합니다.
    Args:
        device_id: 특정 장비 필터 (옵션, 없으면 전체).
        limit: 최대 반환 건수.
    Returns: List[AlertResponse]
    Raises: 500 - DB 오류.
    """
    try:
        query = select(AlertEvent)
        if device_id:
            query = query.where(AlertEvent.device_id == device_id)
        query = query.order_by(AlertEvent.time.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.error("알림 목록 조회 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="알림 목록을 불러오지 못했습니다.")


@router.post("/{alert_id}/acknowledge", status_code=204)
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """
    목적: 알림을 확인 처리합니다 (notified=True).
    Args: alert_id (int) - 알림 ID.
    Raises: 404 - 알림 없음. 500 - DB 오류.
    """
    try:
        alert = await db.get(AlertEvent, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")
        alert.notified = True
        await db.commit()
        logger.info("알림 확인 처리: alert_id=%s", alert_id)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("알림 확인 처리 실패: alert_id=%s, %s", alert_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="알림 확인 처리에 실패했습니다.")
