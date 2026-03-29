from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    time: datetime
    device_id: str
    severity: str
    metric: str | None
    value: float | None
    threshold: float | None
    message: str | None
    notified: bool

    model_config = {"from_attributes": True}
