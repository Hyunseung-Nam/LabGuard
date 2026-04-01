"""
JEIO TECH 항온항습기 RS-232 드라이버.

지원 모델: WBTC / WEVC / MIVC 시리즈 (RS-232 포트 탑재 모델)
통신 설정: 9600 baud, 8N1

프로토콜 (ASCII 명령어 방식):
  온도 현재값 조회: "RT\\r\\n"  → "OK +025.30\\r\\n"
  습도 현재값 조회: "RH\\r\\n"  → "OK +060.20\\r\\n"

⚠️  모델별 프로토콜이 다를 수 있습니다.
    실제 장비 연결 전 제품 매뉴얼의 "RS-232C Communication" 섹션을 확인하세요.
    JEIO TECH 고객지원: https://www.jeiotech.com

연결 방법:
  1. 장비 뒷면 RS-232 포트 확인
  2. USB-to-RS232 어댑터 (FTDI 칩셋 권장) 연결
  3. SERIAL_PORT=auto 설정 시 자동 감지
"""

import logging
import time

import serial
import serial.tools.list_ports

from .base import BaseDriver

logger = logging.getLogger(__name__)

# USB-RS232 어댑터 포트 감지 키워드
RS232_ADAPTER_KEYWORDS = ["usbserial", "ftdi", "prolific", "ch340", "cp210"]

# 명령어 상수
CMD_READ_TEMP = "RT"
CMD_READ_HUMID = "RH"
RESPONSE_TIMEOUT = 3.0   # 초
COMMAND_DELAY = 0.1      # 명령 사이 대기 (초)


class JeioTechDriver(BaseDriver):
    """
    역할: JEIO TECH 항온항습기 RS-232 드라이버.
    책임 범위: ASCII 명령어 전송, 응답 파싱.
    외부 의존성: pyserial.
    """

    def __init__(self):
        self._serial: serial.Serial | None = None

    def detect_port(self) -> str | None:
        """
        목적: USB-RS232 어댑터가 연결된 포트를 자동 감지합니다.
        Returns: 포트 문자열, 없으면 None.
        Side Effects: 없음.
        Raises: 없음.
        """
        for port in serial.tools.list_ports.comports():
            desc = ((port.description or "") + (port.manufacturer or "")).lower()
            if any(k in desc for k in RS232_ADAPTER_KEYWORDS):
                logger.info("RS-232 어댑터 감지: %s (%s)", port.device, port.description)
                return port.device
        logger.debug("RS-232 어댑터를 찾지 못했습니다.")
        return None

    def connect(self, port: str, baud_rate: int = 9600) -> None:
        """
        목적: 항온항습기 RS-232 포트에 연결합니다.
        Args:
            port: 시리얼 포트 경로.
            baud_rate: 통신 속도 (JEIO TECH 기본값 9600).
        Raises: serial.SerialException - 연결 실패 시.
        """
        self._serial = serial.Serial(
            port,
            baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=RESPONSE_TIMEOUT,
        )
        logger.info("JEIO TECH 연결됨: %s @ %d baud", port, baud_rate)

    def _query(self, command: str) -> str | None:
        """
        목적: 명령을 전송하고 응답을 수신합니다.
        Args: command - 전송할 ASCII 명령어.
        Returns: 응답 문자열, 타임아웃이면 None.
        Side Effects: 시리얼 버퍼 읽기/쓰기.
        Raises: RuntimeError - 시리얼 통신 오류.
        """
        try:
            self._serial.reset_input_buffer()
            self._serial.write(f"{command}\r\n".encode("ascii"))
            time.sleep(COMMAND_DELAY)
            response = self._serial.readline().decode("ascii").strip()
            logger.debug("CMD: %r → RESP: %r", command, response)
            return response if response else None
        except serial.SerialException as e:
            raise RuntimeError(f"시리얼 통신 오류: {e}") from e

    def _parse_value(self, response: str | None) -> float | None:
        """
        목적: "OK +025.30" 형태의 응답에서 숫자를 파싱합니다.
        Args: response - 장비 응답 문자열.
        Returns: float 값, 파싱 실패 시 None.
        """
        if not response or not response.startswith("OK"):
            return None
        try:
            return float(response[2:].strip())
        except ValueError:
            logger.warning("값 파싱 실패: %r", response)
            return None

    def read(self) -> dict[str, tuple[float, str]]:
        """
        목적: 온도 및 습도 현재값을 읽습니다.
        Returns: {"temperature": (25.3, "°C"), "humidity": (60.2, "%")} 형태.
        Raises: RuntimeError - 연결되지 않은 상태.
        """
        if not self._serial:
            raise RuntimeError("연결되지 않은 상태에서 read() 호출")

        result = {}

        temp = self._parse_value(self._query(CMD_READ_TEMP))
        if temp is not None:
            result["temperature"] = (temp, "°C")

        humid = self._parse_value(self._query(CMD_READ_HUMID))
        if humid is not None:
            result["humidity"] = (humid, "%")

        return result

    def disconnect(self) -> None:
        """목적: 시리얼 연결을 안전하게 해제합니다."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        logger.info("JEIO TECH 연결 해제.")
