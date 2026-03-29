from fastapi import APIRouter
from app.api.routes import devices, measurements, alerts, dashboard

api_router = APIRouter(prefix="/api")
api_router.include_router(devices.router)
api_router.include_router(measurements.router)
api_router.include_router(alerts.router)
api_router.include_router(dashboard.router)
