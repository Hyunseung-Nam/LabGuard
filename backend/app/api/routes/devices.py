import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    """
    목적: 등록된 장비 전체 목록을 반환합니다.
    Returns: List[DeviceResponse]
    Raises: 500 - DB 오류 시.
    """
    try:
        result = await db.execute(select(Device).order_by(Device.created_at.desc()))
        return result.scalars().all()
    except Exception as e:
        logger.error("장비 목록 조회 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="장비 목록을 불러오지 못했습니다.")


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    목적: 특정 장비 상세 정보를 반환합니다.
    Args: device_id (str) - 장비 UUID.
    Returns: DeviceResponse
    Raises: 404 - 장비 없음. 500 - DB 오류.
    """
    try:
        device = await db.get(Device, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="장비를 찾을 수 없습니다.")
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error("장비 조회 실패: device_id=%s, %s", device_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="장비 정보를 불러오지 못했습니다.")


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    """
    목적: 새 장비를 등록합니다.
    Args: payload (DeviceCreate) - 장비 등록 정보.
    Returns: DeviceResponse - 생성된 장비.
    Raises: 500 - DB 오류.
    """
    try:
        device = Device(**payload.model_dump())
        db.add(device)
        await db.commit()
        await db.refresh(device)
        logger.info("장비 등록: device_id=%s, name=%s", device.id, device.name)
        return device
    except Exception as e:
        await db.rollback()
        logger.error("장비 등록 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="장비 등록에 실패했습니다.")


@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    목적: 장비를 삭제합니다.
    Args: device_id (str) - 삭제할 장비 UUID.
    Raises: 404 - 장비 없음. 500 - DB 오류.
    """
    try:
        device = await db.get(Device, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="장비를 찾을 수 없습니다.")
        await db.delete(device)
        await db.commit()
        logger.info("장비 삭제: device_id=%s", device_id)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("장비 삭제 실패: device_id=%s, %s", device_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="장비 삭제에 실패했습니다.")
