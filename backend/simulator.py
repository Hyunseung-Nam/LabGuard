"""
시뮬레이터: 실제 장비 없이 가짜 측정값을 API로 전송하는 스크립트.

동작:
  1. 테스트 장비 3개를 자동 등록 (이미 있으면 재사용)
  2. 5초마다 각 장비의 측정값을 POST /measurements 로 전송
  3. 10% 확률로 임계치 초과 이상값 주입

실행:
  cd backend
  pip install httpx
  python simulator.py
"""

import logging
import random
import time

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api"
INTERVAL_SECONDS = 5
ANOMALY_PROBABILITY = 0.1  # 10%

# 테스트 장비 정의
DEVICE_TEMPLATES = [
    {
        "name": "온도계-A (시뮬)",
        "location": "실험실 1",
        "protocol": "simulated",
        "config": {},
        "threshold": {"temperature": {"min": 15.0, "max": 35.0}},
    },
    {
        "name": "기압계-B (시뮬)",
        "location": "실험실 2",
        "protocol": "simulated",
        "config": {},
        "threshold": {"pressure": {"min": 990.0, "max": 1030.0}},
    },
    {
        "name": "전압계-C (시뮬)",
        "location": "실험실 3",
        "protocol": "simulated",
        "config": {},
        "threshold": {"voltage": {"min": 210.0, "max": 230.0}},
    },
]

# 측정항목별 정상 범위 및 단위
METRICS = {
    "온도계-A (시뮬)": {
        "metric": "temperature",
        "unit": "°C",
        "normal_mean": 25.0,
        "normal_std": 1.5,
        "anomaly_value": 42.0,
    },
    "기압계-B (시뮬)": {
        "metric": "pressure",
        "unit": "hPa",
        "normal_mean": 1013.0,
        "normal_std": 3.0,
        "anomaly_value": 975.0,
    },
    "전압계-C (시뮬)": {
        "metric": "voltage",
        "unit": "V",
        "normal_mean": 220.0,
        "normal_std": 2.0,
        "anomaly_value": 245.0,
    },
}


def ensure_devices(client: httpx.Client) -> dict[str, str]:
    """
    목적: 테스트 장비가 DB에 없으면 등록하고 device_id 맵을 반환합니다.
    Args: client - httpx 동기 클라이언트.
    Returns: {장비 이름: device_id} 딕셔너리.
    Side Effects: 없는 장비를 POST /devices 로 등록.
    Raises: httpx.HTTPStatusError - API 오류 시.
    """
    try:
        resp = client.get(f"{BASE_URL}/devices")
        resp.raise_for_status()
        existing = {d["name"]: d["id"] for d in resp.json()}
    except Exception as e:
        logger.error("장비 목록 조회 실패: %s", e)
        raise

    device_ids = {}
    for template in DEVICE_TEMPLATES:
        name = template["name"]
        if name in existing:
            device_ids[name] = existing[name]
            logger.info("기존 장비 재사용: %s (%s)", name, existing[name])
        else:
            try:
                resp = client.post(f"{BASE_URL}/devices", json=template)
                resp.raise_for_status()
                created = resp.json()
                device_ids[name] = created["id"]
                logger.info("장비 등록 완료: %s (%s)", name, created["id"])
            except Exception as e:
                logger.error("장비 등록 실패: %s - %s", name, e)
                raise

    return device_ids


def generate_value(device_name: str) -> tuple[float, float]:
    """
    목적: 장비 이름에 맞는 raw/filtered 측정값을 생성합니다.
    Args: device_name - 장비 이름 (METRICS 키).
    Returns: (raw_value, filtered_value) 튜플.
    Side Effects: 없음 (10% 확률로 이상값 반환).
    Raises: 없음.
    """
    spec = METRICS[device_name]
    is_anomaly = random.random() < ANOMALY_PROBABILITY

    if is_anomaly:
        raw = spec["anomaly_value"] + random.uniform(-0.5, 0.5)
        logger.warning("이상값 주입: %s → %.2f %s", device_name, raw, spec["unit"])
    else:
        raw = random.gauss(spec["normal_mean"], spec["normal_std"])

    # 간단한 이동평균 필터 시뮬레이션 (raw의 소음 10% 제거)
    filtered = raw * 0.9 + spec["normal_mean"] * 0.1

    return round(raw, 3), round(filtered, 3)


def send_measurement(client: httpx.Client, device_id: str, device_name: str) -> None:
    """
    목적: 측정값 1건을 생성해 POST /measurements 로 전송합니다.
    Args:
        client - httpx 동기 클라이언트.
        device_id - 장비 UUID.
        device_name - 장비 이름 (측정 스펙 조회용).
    Returns: 없음.
    Side Effects: API 호출 및 로그 출력.
    Raises: 없음 (오류는 로그로만 처리).
    """
    spec = METRICS[device_name]
    raw, filtered = generate_value(device_name)

    payload = {
        "device_id": device_id,
        "metric": spec["metric"],
        "raw_value": raw,
        "filtered_value": filtered,
        "unit": spec["unit"],
    }

    try:
        resp = client.post(f"{BASE_URL}/measurements", json=payload)
        resp.raise_for_status()
        logger.info(
            "전송 완료: %-20s %s=%.3f %s",
            device_name,
            spec["metric"],
            raw,
            spec["unit"],
        )
    except Exception as e:
        logger.error("전송 실패: %s - %s", device_name, e)


def run() -> None:
    """
    목적: 시뮬레이터 메인 루프. Ctrl+C로 종료.
    Args: 없음.
    Returns: 없음.
    Side Effects: 주기적으로 API 호출, 로그 출력.
    Raises: 없음 (KeyboardInterrupt는 정상 종료로 처리).
    """
    logger.info("=== LabGuard 시뮬레이터 시작 (간격: %ds) ===", INTERVAL_SECONDS)

    with httpx.Client(timeout=10.0) as client:
        # 백엔드 연결 확인
        try:
            client.get(f"{BASE_URL}/devices").raise_for_status()
        except Exception:
            logger.error("백엔드에 연결할 수 없습니다: %s", BASE_URL)
            logger.error("docker compose up -d 실행 후 다시 시도하세요.")
            return

        device_ids = ensure_devices(client)
        logger.info("시뮬레이션 대상 장비: %d개", len(device_ids))
        logger.info("Ctrl+C 로 종료\n")

        try:
            while True:
                for name, device_id in device_ids.items():
                    send_measurement(client, device_id, name)
                time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("시뮬레이터 종료.")


if __name__ == "__main__":
    run()
