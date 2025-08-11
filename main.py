from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.vo import auth_vo, signal_data_vo
from database import engine
from app.controller import auth, home, report,dashbord
from fastapi.middleware.cors import CORSMiddleware
import multiprocessing
import time
from app.services.car_track import multi_feed_object_detection
app = FastAPI()

# Create database tables
auth_vo.Base.metadata.create_all(bind=engine)
signal_data_vo.Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(report.router)
app.include_router(dashbord.router)

# Define the video and mask paths
video_paths = ["tra.mp4", "tra.mp4", "tra.mp4", "tra.mp4"]
mask_paths = ["mask2.png", "mask2.png", "mask2.png", "mask2.png"]

# Define a wrapper function to pass correct arguments to the process
def start_object_detection():
    multi_feed_object_detection(video_paths, mask_paths)

# Function to start both scripts in parallel
def start_background_scripts():
    p1 = multiprocessing.Process(target=start_object_detection)
    p1.start()


    # Store process references to ensure they don't get garbage collected
    app.state.script_processes = [p1]

@app.on_event("startup")
def startup_event():
    print("Starting background scripts...")
    start_background_scripts()

@app.on_event("shutdown")
def shutdown_event():
    print("Stopping background scripts...")
    for process in app.state.script_processes:
        process.terminate()
