from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    역할: 환경변수 기반 애플리케이션 설정 관리.
    책임 범위: 모든 설정값의 단일 진입점. 코드 내 하드코딩 금지.
    외부 의존성: pydantic-settings, .env 파일.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://labguard:labguard@localhost:5432/labguard"
    SECRET_KEY: str = "change-me-in-production"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # 알림 쿨다운 (동일 장비 중복 알림 방지)
    ALERT_COOLDOWN_SECONDS: int = 300


settings = Settings()
