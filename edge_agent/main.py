"""
LabGuard Edge Agent

실험 장비(항온항습기 등)에서 RS-232로 측정값을 읽어 LabGuard 서버로 전송합니다.

실행:
  cd edge_agent
  pip install -r requirements.txt
  cp .env.example .env   # DEVICE_ID 설정 후 실행
  python main.py

지원 드라이버:
  arduino_json  — Arduino 에뮬레이터 (테스트용)
  jeiotech      — JEIO TECH 항온항습기 (RS-232)
"""

import logging
import time

import httpx

from config import settings
from drivers import get_driver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def post_measurement(client: httpx.Client, metric: str, value: float, unit: str) -> None:
    """
    목적: 측정값 1건을 LabGuard 백엔드로 전송합니다.
    Args:
        client: httpx 동기 클라이언트.
        metric: 측정 항목명 (temperature, humidity 등).
        value: 측정값.
        unit: 단위 문자열 (°C, % 등).
    Returns: 없음.
    Side Effects: POST /measurements API 호출.
    Raises: 없음 (오류는 로그 처리).
    """
    payload = {
        "device_id": settings.DEVICE_ID,
        "metric": metric,
        "raw_value": value,
        "filtered_value": value,
        "unit": unit,
    }
    try:
        resp = client.post(f"{settings.API_URL}/measurements", json=payload)
        resp.raise_for_status()
        logger.info("전송: %s=%.2f%s", metric, value, unit)
    except Exception as e:
        logger.error("전송 실패: %s", e)


def run() -> None:
    """
    목적: Edge Agent 메인 루프. 장비 연결 → 측정 → 전송을 반복합니다.
    Args: 없음.
    Returns: 없음.
    Side Effects: 주기적으로 API 호출, 로그 출력.
    Raises: 없음 (KeyboardInterrupt는 정상 종료로 처리).
    """
    logger.info("=== LabGuard Edge Agent 시작 ===")
    logger.info("장비 ID : %s", settings.DEVICE_ID)
    logger.info("드라이버: %s | 포트: %s | 주기: %ds",
                settings.DRIVER, settings.SERIAL_PORT, settings.POLL_INTERVAL)

    driver = get_driver(settings.DRIVER)

    with httpx.Client(timeout=10.0) as client:
        while True:
            try:
                # 포트 결정 (auto면 드라이버가 자동 감지)
                if settings.SERIAL_PORT == "auto":
                    port = driver.detect_port()
                    if not port:
                        logger.warning("장비를 찾을 수 없습니다. %ds 후 재시도...", settings.RETRY_INTERVAL)
                        time.sleep(settings.RETRY_INTERVAL)
                        continue
                else:
                    port = settings.SERIAL_PORT

                logger.info("포트 연결: %s", port)
                driver.connect(port, settings.SERIAL_BAUD_RATE)

                # 측정 루프
                while True:
                    measurements = driver.read()
                    for metric, (value, unit) in measurements.items():
                        post_measurement(client, metric, value, unit)
                    time.sleep(settings.POLL_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Edge Agent 종료.")
                break
            except Exception as e:
                logger.error("오류: %s — %ds 후 재연결...", e, settings.RETRY_INTERVAL)
                try:
                    driver.disconnect()
                except Exception:
                    pass
                time.sleep(settings.RETRY_INTERVAL)


if __name__ == "__main__":
    run()
