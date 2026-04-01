"""
장비 드라이버 추상 기본 클래스.
새 장비 지원 추가 시 이 클래스를 상속합니다.
"""

from abc import ABC, abstractmethod


class BaseDriver(ABC):
    """
    역할: RS-232 계측 장비 드라이버 인터페이스.
    책임 범위: 포트 감지, 연결, 측정값 읽기, 연결 해제.
    외부 의존성: pyserial.
    """

    @abstractmethod
    def detect_port(self) -> str | None:
        """
        목적: 연결된 장비의 시리얼 포트를 자동 감지합니다.
        Returns: 포트 문자열 (예: /dev/tty.usbserial-XXXX), 없으면 None.
        """
        ...

    @abstractmethod
    def connect(self, port: str, baud_rate: int) -> None:
        """
        목적: 지정 포트로 시리얼 연결을 엽니다.
        Args:
            port: 시리얼 포트 경로.
            baud_rate: 통신 속도.
        Raises: serial.SerialException - 연결 실패 시.
        """
        ...

    @abstractmethod
    def read(self) -> dict[str, tuple[float, str]]:
        """
        목적: 장비에서 측정값을 읽습니다.
        Returns: {"temperature": (25.3, "°C"), "humidity": (60.2, "%")} 형태.
        Raises: RuntimeError - 연결되지 않은 상태에서 호출 시.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """목적: 시리얼 연결을 안전하게 해제합니다."""
        ...
