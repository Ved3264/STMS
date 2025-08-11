from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.vo.signal_data_vo import TrafficSignal  # Adjust import based on your project structure
from database import SessionLocal  # Adjust import based on your database setup

# Create a new router for dashboard APIs
router = APIRouter(prefix="/dash", tags=["dash"])
template = Jinja2Templates("templates")
# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def dashbord(request: Request):
    return template.TemplateResponse('dash.html', {"request": request})

@router.get("/api/latest-signal")
async def get_latest_signal(db: Session = Depends(get_db)):
    """
    Fetch the most recent traffic signal data from the database, including last_signal_id.
    """
    latest = (
        db.query(TrafficSignal)
        .order_by(desc(TrafficSignal.date), desc(TrafficSignal.save_time))
        .first()
    )
    if latest:
        return {
            "signal_id": latest.signal_id,
            "total_vehicle": latest.total_vehicle,
            "total_car": latest.total_car,
            "total_bus": latest.total_bus,
            "total_truck": latest.total_truck,
            "total_motorbike": latest.total_motorbike,
            "time": latest.time,
            "last_signal_id": latest.last_signal_id  # Added last_signal_id
        }
    return {}