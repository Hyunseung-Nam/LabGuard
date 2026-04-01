"""
Arduino JSON 드라이버 (에뮬레이터 테스트용).

Arduino가 Serial로 {"T": 25.3, "H": 60.2} 형태의 JSON을 전송할 때 사용합니다.
실제 항온항습기 없이 Edge Agent 통신 레이어를 테스트하기 위한 드라이버입니다.

Arduino 스케치: edge_agent/emulator/emulator.ino
"""

import json
import logging

import serial
import serial.tools.list_ports

from .base import BaseDriver

logger = logging.getLogger(__name__)

# Arduino가 USB로 인식될 때 포트 설명에 포함되는 키워드
ARDUINO_KEYWORDS = ["usbmodem", "usbserial", "arduino", "ch340", "cp210", "ftdi"]


class ArduinoJsonDriver(BaseDriver):
    """
    역할: Arduino 에뮬레이터 드라이버.
    책임 범위: JSON 라인 읽기 및 파싱.
    외부 의존성: pyserial.
    """

    def __init__(self):
        self._serial: serial.Serial | None = None

    def detect_port(self) -> str | None:
        """
        목적: 연결된 Arduino 포트를 자동 감지합니다.
        Returns: 포트 문자열, 없으면 None.
        Side Effects: 없음.
        Raises: 없음.
        """
        for port in serial.tools.list_ports.comports():
            desc = ((port.description or "") + (port.manufacturer or "")).lower()
            if any(k in desc for k in ARDUINO_KEYWORDS):
                logger.info("Arduino 감지: %s (%s)", port.device, port.description)
                return port.device
        logger.debug("Arduino 포트를 찾지 못했습니다.")
        return None

    def connect(self, port: str, baud_rate: int = 9600) -> None:
        """
        목적: Arduino 시리얼 포트에 연결합니다.
        Args:
            port: 시리얼 포트 경로.
            baud_rate: 통신 속도 (기본 9600).
        Raises: serial.SerialException - 연결 실패 시.
        """
        self._serial = serial.Serial(port, baud_rate, timeout=5)
        logger.info("Arduino 연결됨: %s @ %d baud", port, baud_rate)

    def read(self) -> dict[str, tuple[float, str]]:
        """
        목적: Arduino에서 JSON 한 줄을 읽어 측정값을 파싱합니다.
        Returns: {"temperature": (25.3, "°C"), "humidity": (60.2, "%")} 형태.
        Raises: RuntimeError - 연결되지 않은 상태 또는 시리얼 오류.
        """
        if not self._serial:
            raise RuntimeError("연결되지 않은 상태에서 read() 호출")

        line = ""
        try:
            line = self._serial.readline().decode("utf-8").strip()
            if not line:
                return {}

            data = json.loads(line)
            result = {}
            if "T" in data:
                result["temperature"] = (float(data["T"]), "°C")
            if "H" in data:
                result["humidity"] = (float(data["H"]), "%")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("파싱 오류: %s — 원본: %r", e, line)
            return {}
        except serial.SerialException as e:
            raise RuntimeError(f"시리얼 읽기 실패: {e}") from e

    def disconnect(self) -> None:
        """목적: 시리얼 연결을 안전하게 해제합니다."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        logger.info("Arduino 연결 해제.")
