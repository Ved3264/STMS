from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.vo.signal_data_vo import TrafficSignal
from database import SessionLocal

# FastAPI app
router = APIRouter(prefix='/report', tags=['report'])
template = Jinja2Templates("templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def report(request: Request):
    return template.TemplateResponse('report.html', {"request": request})

@router.get("/api/data")
async def get_report_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    try:
        # Convert string dates to datetime.date
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Query the database for the selected date range
    traffic_data = (
        db.query(TrafficSignal)
        .filter(TrafficSignal.date >= start_date_obj, TrafficSignal.date <= end_date_obj)
        .order_by(TrafficSignal.date, TrafficSignal.save_time)
        .all()
    )

    if not traffic_data:
        raise HTTPException(status_code=404, detail="No data found for the selected date range.")

    # Extracting labels and data from the database
    labels = [entry.save_time.strftime("%H:%M") for entry in traffic_data]
    
    vehicle_data = [
        {"label": "Cars", "data": [entry.total_car for entry in traffic_data], "color": "rgba(255, 99, 132, 1)"},
        {"label": "Buses", "data": [entry.total_bus for entry in traffic_data], "color": "rgba(54, 162, 235, 1)"},
        {"label": "Trucks", "data": [entry.total_truck for entry in traffic_data], "color": "rgba(255, 206, 86, 1)"},
        {"label": "Motorbikes", "data": [entry.total_motorbike for entry in traffic_data], "color": "rgba(75, 192, 192, 1)"},
    ]

    vehicle_counts = [entry.total_vehicle for entry in traffic_data]  # Bar chart
    total_vehicles = [sum([entry.total_car, entry.total_bus, entry.total_truck, entry.total_motorbike]) for entry in traffic_data]  # Area chart

    response = {
        "labels": labels,
        "vehicleData": vehicle_data,  # Line Chart
        "vehicleCounts": vehicle_counts,  # Bar Chart
        "totalVehicles": total_vehicles,  # Area Chart
        "colors": ["red", "blue", "green", "orange"],
        "areaChartColor": "rgba(0, 123, 255, 0.5)"
    }

    return response