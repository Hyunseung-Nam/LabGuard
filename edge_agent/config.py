"""
Edge Agent 설정.
모든 값은 .env 파일 또는 환경변수에서 읽습니다.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LabGuard 서버
    API_URL: str = "http://localhost:8000/api"
    DEVICE_ID: str  # LabGuard에 등록된 장비 UUID (필수)

    # 시리얼 통신
    SERIAL_PORT: str = "auto"        # "auto" 또는 "/dev/tty.usbserial-XXXX"
    SERIAL_BAUD_RATE: int = 9600
    DRIVER: str = "arduino_json"     # "arduino_json" | "jeiotech"

    # 동작 설정
    POLL_INTERVAL: int = 5           # 측정 주기 (초)
    RETRY_INTERVAL: int = 10         # 연결 실패 시 재시도 대기 (초)

    model_config = {"env_file": ".env"}


settings = Settings()
