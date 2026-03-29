from datetime import datetime
from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    device_id: str
    metric: str
    raw_value: float | None = None
    filtered_value: float | None = None
    unit: str | None = None


class MeasurementResponse(BaseModel):
    time: datetime
    device_id: str
    metric: str
    raw_value: float | None
    filtered_value: float | None
    unit: str | None

    model_config = {"from_attributes": True}
