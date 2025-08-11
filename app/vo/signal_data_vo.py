from sqlalchemy import Column, Integer, Time, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TrafficSignal(Base):
    __tablename__ = "traffic_signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, nullable=False)
    total_vehicle = Column(Integer, nullable=False)
    total_car  = Column(Integer, nullable=False)
    total_bus = Column(Integer, nullable=False)
    total_truck = Column(Integer, nullable=False)
    total_motorbike = Column(Integer, nullable=False)
    last_signal_id = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    save_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)