from .arduino_json import ArduinoJsonDriver
from .jeiotech import JeioTechDriver
from .base import BaseDriver

DRIVERS: dict[str, type[BaseDriver]] = {
    "arduino_json": ArduinoJsonDriver,
    "jeiotech": JeioTechDriver,
}


def get_driver(name: str) -> BaseDriver:
    """
    목적: 드라이버 이름으로 드라이버 인스턴스를 반환합니다.
    Args: name - 드라이버 이름 ("arduino_json" | "jeiotech").
    Returns: BaseDriver 인스턴스.
    Raises: ValueError - 알 수 없는 드라이버 이름.
    """
    cls = DRIVERS.get(name)
    if not cls:
        raise ValueError(f"알 수 없는 드라이버: '{name}'. 사용 가능: {list(DRIVERS.keys())}")
    return cls()
