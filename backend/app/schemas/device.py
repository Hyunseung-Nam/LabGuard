from datetime import datetime
from pydantic import BaseModel


class DeviceCreate(BaseModel):
    name: str
    location: str | None = None
    protocol: str
    config: dict | None = None
    threshold: dict | None = None


class DeviceResponse(BaseModel):
    id: str
    name: str
    location: str | None
    protocol: str
    config: dict | None
    threshold: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
