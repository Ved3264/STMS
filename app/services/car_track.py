import datetime
import cv2
from sqlalchemy import desc
import torch
import math
from ultralytics import YOLO
from app.services.tracker import YOLOTracker
import time
import database
from database import SessionLocal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.vo.signal_data_vo import TrafficSignal
import numpy as np  # Added for blank frame creation

def time_counting(cap, s_time, total_v):
    capacity = int(cap)
    signal_time = int(s_time)
    total_vehicle = int(total_v)
    new_time = 0
    trafic_data = []
    Density = total_vehicle / capacity
            
    if 0.0 <= Density <= 0.5:
        new_time = signal_time * 1
    elif 0.5 <= Density <= 0.8:
        new_time = signal_time * 1.2
    elif 0.8 <= Density <= 1.0:
        new_time = signal_time * 1.5
    else:  # Density > 1.0
        new_time = signal_time * 2
            
    trafic_data.append({
        "Density": round(Density, 2),
        "SignalTime": round(new_time, 2)
    })
    return trafic_data

def multi_feed_object_detection(video_paths, mask_paths):
    model = YOLO('yolov8n.pt')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    caps = [cv2.VideoCapture(path) for path in video_paths]
    frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(caps[0].get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width * 2, frame_height * 2))  # 2x2 grid

    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", 
                  "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", 
                  "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", 
                  "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", 
                  "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", 
                  "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", 
                  "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", 
                  "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", 
                  "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]

    detect_class = ["bicycle", "car", "motorbike", "bus", "truck"]
    limits_list = [
        [400, 485, 1250, 485], 
        [400, 485, 1250, 485], 
        [400, 485, 1250, 485], 
        [400, 485, 1250, 485]
    ]
    
    mask_paths = ["mask2.png", "mask2.png", "mask2.png", "mask2.png"]
    masks = [cv2.imread(mask) if mask else None for mask in mask_paths]
    trackers = [YOLOTracker() for _ in range(4)]

    total_counts = [[] for _ in range(4)]
    car_counts = [[] for _ in range(4)]
    bike_counts = [[] for _ in range(4)]
    truck_counts = [[] for _ in range(4)]
    bus_counts = [[] for _ in range(4)]
    bicycle_counts = [[] for _ in range(4)]

    db = SessionLocal()

    current_time = datetime.now()
    current_date = datetime.today().strftime('%Y-%m-%d')
    new_time = current_time + timedelta(seconds=20)
    formatted_time = new_time.strftime('%H:%M:%S')
    new_traffic_signal = TrafficSignal(
        signal_id=1,
        total_vehicle=0,
        total_car=0,
        total_bus=0,
        total_truck=0,
        total_motorbike=0,
        last_signal_id=1,
        time=20,
        save_time=formatted_time,
        date=current_date
    )
    db.add(new_traffic_signal)
    db.commit()
    db.refresh(new_traffic_signal)

    while True:
        frame_count = 0
        frames = []
        success_flags = []

        data = db.query(TrafficSignal).filter(TrafficSignal.signal_id == 1).order_by(desc(TrafficSignal.id)).first()
        current_time = datetime.now()
        formatted_time1 = current_time.strftime('%H:%M:%S')

        if formatted_time1 >= data.save_time.strftime('%H:%M:%S'):
            signal_id_next = int(data.last_signal_id)
            total_len = signal_id_next - 1
            if signal_id_next == 4:
                signal_id_next = 1
            else:
                signal_id_next = signal_id_next + 1
            dyanmic_time = time_counting(50, 20, len(total_counts[total_len]))
            signal_time = dyanmic_time[0]["SignalTime"]

            new_time = current_time + timedelta(seconds=signal_time)
            formatted_time = new_time.strftime('%H:%M:%S')
            current_date = datetime.today().strftime('%Y-%m-%d')
            new_traffic_signal = TrafficSignal(
                signal_id=1,
                total_vehicle=len(total_counts[total_len]),
                total_car=len(car_counts[total_len]),
                total_bus=len(bus_counts[total_len]),
                total_truck=len(truck_counts[total_len]),
                total_motorbike=len(bike_counts[total_len]),
                last_signal_id=signal_id_next,
                time=signal_time,
                save_time=formatted_time,
                date=current_date  
            )
            total_counts[total_len].clear()
            car_counts[total_len].clear()
            bus_counts[total_len].clear()
            bike_counts[total_len].clear()
            total_counts[total_len].clear()
            db.add(new_traffic_signal)
            db.commit()
            db.refresh(new_traffic_signal)

        for i, cap in enumerate(caps):
            start_timer = time.time()
            success, img = cap.read()
            if not success:
                success_flags.append(False)
                frames.append(None)
            else:
                success_flags.append(True)
                frames.append(img)

        if not any(success_flags):
            print("All video streams have ended.")
            break

        # Replace None frames with blank images to avoid concatenation errors
        for i in range(4):
            if frames[i] is None:
                frames[i] = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

        for i in range(4):
            if not success_flags[i]:
                continue

            img = frames[i]
            if masks[i] is not None:
                imgRegion = cv2.bitwise_and(img, masks[i])
            else:
                imgRegion = img

            if frame_count % 5 == 0:
                results = model(imgRegion, stream=True)
                detections = []

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])
                    current_class = classNames[cls]

                    if current_class in detect_class and conf > 0.4:
                        detections.append([x1, y1, x2, y2, conf, cls])

            result_track = trackers[i].update(detections)
            end_time = time.time()
            current_fps = 1 / (end_time - start_timer)
            
            limits = limits_list[i]
            cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), 8)

            for result in result_track:
                x1, y1, x2, y2, confidence, object_id, class_id = result
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 5)
                cv2.putText(img, f'ID: {object_id}, {classNames[class_id]}', (max(0, x1), max(35, y1)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                w, h = x2 - x1, y2 - y1
                cx, cy = x1 + w // 2, y1 + h // 2
                cv2.circle(img, (cx, cy), 20, (0, 110, 255), -1)

                if limits[0] < cx < limits[2] and limits[1] - 15 < cy < limits[1] + 15:
                    if object_id not in total_counts[i]:
                        total_counts[i].append(object_id)
                        if classNames[class_id] == "car":
                            car_counts[i].append(object_id)
                        elif classNames[class_id] == "bus":
                            bus_counts[i].append(object_id)
                        elif classNames[class_id] == "truck":
                            truck_counts[i].append(object_id)
                        elif classNames[class_id] == "motorbike":
                            bike_counts[i].append(object_id)
                        elif classNames[class_id] == "bicycle":
                            bicycle_counts[i].append(object_id)

            cv2.putText(img, f'Total: {len(total_counts[i])}, Car: {len(car_counts[i])}, Truck: {len(truck_counts[i])}, '
                             f'Bus: {len(bus_counts[i])}, Bike: {len(bike_counts[i])}',
                        (255, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Combine frames into a 2x2 grid
        combined = cv2.vconcat([cv2.hconcat(frames[:2]), cv2.hconcat(frames[2:])])
        frame_count += 1

        # Write the combined frame to the output video
        out_writer.write(combined)

        # Resize the combined frame for display
        display_width = 1280  # Adjust this value based on your screen size
        display_height = int(display_width * (frame_height * 2) / (frame_width * 2))
        combined_resized = cv2.resize(combined, (display_width, display_height))
        cv2.imshow("Multi-Feed Object Detection", combined_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Video playback terminated by user.")
            print(end_time - start_timer)
            break

    for cap in caps:
        cap.release()
    out_writer.release()  # Release the video writer
    cv2.destroyAllWindows()
    db.close()  # Close the database session