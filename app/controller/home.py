from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.vo.signal_data_vo import TrafficSignal
from database import SessionLocal

router = APIRouter(prefix='/home', tags=['home'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/chart1-data")
async def get_chart1_data(db: Session = Depends(get_db)):
    """ Line Chart: Traffic trend over time """
    data = db.query(TrafficSignal).order_by(desc(TrafficSignal.save_time)).limit(10).all()
    
    labels = [d.save_time.strftime('%H:%M:%S') for d in data]  # X-axis: save_time
    total_vehicles = [d.total_vehicle for d in data]
    total_cars = [d.total_car for d in data]
    total_buses = [d.total_bus for d in data]
    total_trucks = [d.total_truck for d in data]
    total_motorbikes = [d.total_motorbike for d in data]

    return {
        "labels": labels,
        "datasets": [
            {"label": "Total Vehicles", "data": total_vehicles, "color": "#FF0000"},
            {"label": "Cars", "data": total_cars, "color": "#36A2EB"},
            {"label": "Buses", "data": total_buses, "color": "#FFCE56"},
            {"label": "Trucks", "data": total_trucks, "color": "#4BC0C0"},
            {"label": "Motorbikes", "data": total_motorbikes, "color": "#9966FF"},
        ],
    }

@router.get("/api/chart2-data")
async def get_chart2_data(db: Session = Depends(get_db)):
    """ Pie Chart: Vehicle type distribution at a specific time """
    latest_data = db.query(TrafficSignal).order_by(TrafficSignal.save_time.desc()).first()
    if not latest_data:
        return {"labels": [], "values": []}

    labels = ["Car", "Bus", "Truck", "Motorbike"]
    values = [
        latest_data.total_car,
        latest_data.total_bus,
        latest_data.total_truck,
        latest_data.total_motorbike,
    ]
    return {
        "labels": labels,
        "values": values,
        "time": latest_data.save_time.strftime('%H:%M:%S'),
        "colors": ["#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
    }

@router.get("/api/chart3-data")
async def get_chart3_data(db: Session = Depends(get_db)):
    """ Bar Chart: Comparing vehicle types across signals """
    data = db.query(TrafficSignal).order_by(desc(TrafficSignal.signal_id)).limit(10).all()
    
    labels = [f"Signal {d.signal_id}" for d in data]  # X-axis: signal_id
    total_cars = [d.total_car for d in data]
    total_buses = [d.total_bus for d in data]
    total_trucks = [d.total_truck for d in data]
    total_motorbikes = [d.total_motorbike for d in data]

    return {
        "labels": labels,
        "datasets": [
            {"label": "Cars", "data": total_cars, "color": "#36A2EB"},
            {"label": "Buses", "data": total_buses, "color": "#FFCE56"},
            {"label": "Trucks", "data": total_trucks, "color": "#4BC0C0"},
            {"label": "Motorbikes", "data": total_motorbikes, "color": "#9966FF"},
        ],
    }

@router.get("/api/chart4-data")
async def get_chart4_data(db: Session = Depends(get_db)):
    """ Radar Chart: Traffic composition at a specific time """
    latest_data = db.query(TrafficSignal).order_by(TrafficSignal.save_time.desc()).first()
    if not latest_data:
        return {"labels": [], "values": []}

    labels = ["Car", "Bus", "Truck", "Motorbike"]
    values = [
        latest_data.total_car,
        latest_data.total_bus,
        latest_data.total_truck,
        latest_data.total_motorbike,
    ]
    return {"labels": labels, "values": values}
