import random
import os

def detect_objects(image_path: str) -> dict:
    """
    Simulates YOLOv11 vehicle/road user detection and ByteTrack tracking.
    Uses filename hints to make testing of specific violations deterministic,
    otherwise generates a natural, realistic traffic scene.
    """
    filename = os.path.basename(image_path).lower()
    
    # Standard classes: "Car", "Motorcycle", "Truck", "Bus", "Auto-rickshaw", "Pedestrian"
    # We return list of bounding boxes: [x_min, y_min, x_max, y_max, label, confidence, tracker_id]
    
    detections = []
    
    if "helmet" in filename:
        # Motorcycle with helmet violation
        detections = [
            {"box": [200, 300, 350, 600], "label": "Motorcycle", "confidence": 0.94, "track_id": 1},
            {"box": [240, 220, 310, 350], "label": "Rider", "confidence": 0.96, "track_id": 2},
            {"box": [250, 220, 290, 270], "label": "Head_No_Helmet", "confidence": 0.98, "track_id": 3}
        ]
    elif "seatbelt" in filename:
        # Car with seatbelt violation
        detections = [
            {"box": [100, 150, 500, 550], "label": "Car", "confidence": 0.97, "track_id": 4},
            {"box": [220, 220, 380, 450], "label": "Driver_No_Seatbelt", "confidence": 0.92, "track_id": 5}
        ]
    elif "triple" in filename:
        # Triple riding
        detections = [
            {"box": [180, 280, 380, 620], "label": "Motorcycle", "confidence": 0.95, "track_id": 6},
            {"box": [200, 200, 290, 320], "label": "Rider_1", "confidence": 0.91, "track_id": 7},
            {"box": [230, 210, 310, 350], "label": "Rider_2", "confidence": 0.89, "track_id": 8},
            {"box": [260, 220, 330, 380], "label": "Rider_3", "confidence": 0.88, "track_id": 9}
        ]
    elif "wrong" in filename:
        # Wrong side driving
        detections = [
            {"box": [150, 250, 320, 580], "label": "Car", "confidence": 0.96, "track_id": 10, "trajectory": [[400, 580], [350, 480], [300, 380], [250, 250]]}
        ]
    elif "stopline" in filename:
        # Stop-line violation
        detections = [
            {"box": [300, 400, 550, 700], "label": "Car", "confidence": 0.98, "track_id": 11},
            {"box": [0, 480, 800, 490], "label": "Stop_Line", "confidence": 1.0, "track_id": 0}
        ]
    elif "redlight" in filename:
        # Red-light violation
        detections = [
            {"box": [300, 350, 480, 650], "label": "Auto-rickshaw", "confidence": 0.94, "track_id": 12},
            {"box": [450, 100, 500, 250], "label": "Red_Light_Signal", "confidence": 0.99, "track_id": 0}
        ]
    elif "parking" in filename:
        # Illegal parking
        detections = [
            {"box": [50, 300, 400, 680], "label": "Car", "confidence": 0.95, "track_id": 13},
            {"box": [30, 200, 150, 280], "label": "No_Parking_Sign", "confidence": 0.99, "track_id": 0}
        ]
    else:
        # Random traffic scene generators
        scenario = random.choice(["ok_traffic", "helmet_violation", "seatbelt_violation", "wrong_side", "triple_riding"])
        if scenario == "ok_traffic":
            detections = [
                {"box": [100, 200, 350, 450], "label": "Car", "confidence": 0.98, "track_id": 14},
                {"box": [450, 250, 600, 500], "label": "Auto-rickshaw", "confidence": 0.96, "track_id": 15},
                {"box": [280, 180, 380, 320], "label": "Pedestrian", "confidence": 0.89, "track_id": 16}
            ]
        elif scenario == "helmet_violation":
            detections = [
                {"box": [200, 300, 350, 600], "label": "Motorcycle", "confidence": 0.94, "track_id": 17},
                {"box": [240, 220, 310, 350], "label": "Rider", "confidence": 0.96, "track_id": 18},
                {"box": [250, 220, 270, 260], "label": "Head_No_Helmet", "confidence": 0.95, "track_id": 19}
            ]
        elif scenario == "seatbelt_violation":
            detections = [
                {"box": [100, 150, 500, 550], "label": "Car", "confidence": 0.97, "track_id": 20},
                {"box": [220, 220, 380, 450], "label": "Driver_No_Seatbelt", "confidence": 0.93, "track_id": 21}
            ]
        elif scenario == "wrong_side":
            detections = [
                {"box": [150, 250, 320, 580], "label": "Car", "confidence": 0.96, "track_id": 22, "trajectory": [[400, 580], [350, 480], [300, 380], [250, 250]]}
            ]
        elif scenario == "triple_riding":
            detections = [
                {"box": [180, 280, 380, 620], "label": "Motorcycle", "confidence": 0.95, "track_id": 23},
                {"box": [200, 200, 290, 320], "label": "Rider_1", "confidence": 0.91, "track_id": 24},
                {"box": [230, 210, 310, 350], "label": "Rider_2", "confidence": 0.89, "track_id": 25},
                {"box": [260, 220, 330, 380], "label": "Rider_3", "confidence": 0.88, "track_id": 26}
            ]
            
    return {
        "detections": detections,
        "filename": filename
    }
