def check_violations(detections: list) -> dict:
    """
    Evaluates traffic rules based on detected objects, bounding boxes, labels, and tracking trajectories.
    """
    has_violation = False
    violation_type = "No Violation"
    explanation = "All traffic rules are complied with."
    confidence = 1.0
    vehicle_type = "None"
    
    # 1. Stop Line Violation
    stop_line_box = None
    for d in detections:
        if d["label"] == "Stop_Line":
            stop_line_box = d["box"]
            break
            
    if stop_line_box:
        # Check if any vehicle overlaps/crosses the stop line y-coordinate
        stop_line_y = stop_line_box[1] # Using y_min
        for d in detections:
            if d["label"] in ["Car", "Motorcycle", "Auto-rickshaw", "Truck", "Bus"]:
                vehicle_y_max = d["box"][3]
                if vehicle_y_max > stop_line_y:
                    has_violation = True
                    violation_type = "Stop Line Violation"
                    vehicle_type = d["label"]
                    confidence = d["confidence"]
                    explanation = f"{d['label']} (ID {d['track_id']}) crossed the stop line during a red signal."
                    break

    # 2. Red Light Violation
    has_red_light = any(d["label"] == "Red_Light_Signal" for d in detections)
    if has_red_light and not has_violation:
        for d in detections:
            if d["label"] in ["Car", "Motorcycle", "Auto-rickshaw", "Truck", "Bus"]:
                # Check if moving beyond signal
                vehicle_y = d["box"][1]
                if vehicle_y > 300: # Simple region crossing simulation
                    has_violation = True
                    violation_type = "Red Light Violation"
                    vehicle_type = d["label"]
                    confidence = d["confidence"]
                    explanation = f"{d['label']} (ID {d['track_id']}) entered the junction crossing the red signal boundary."
                    break

    # 3. Triple Riding (Motorcycle with >= 3 riders)
    motorcycle_count = sum(1 for d in detections if d["label"] == "Motorcycle")
    riders_count = sum(1 for d in detections if d["label"].startswith("Rider"))
    if motorcycle_count > 0 and riders_count >= 3 and not has_violation:
        has_violation = True
        violation_type = "Triple Riding"
        vehicle_type = "Motorcycle"
        # Combine confidence of riders
        confidence = min(0.98, sum(d["confidence"] for d in detections if d["label"].startswith("Rider")) / riders_count)
        explanation = f"Detected {riders_count} riders on a single motorcycle, violating two-wheeler passenger limits."

    # 4. Helmet Violation
    has_no_helmet = any(d["label"] == "Head_No_Helmet" for d in detections)
    if has_no_helmet and not has_violation:
        has_violation = True
        violation_type = "Helmet Violation"
        vehicle_type = "Motorcycle"
        helmet_detection = next(d for d in detections if d["label"] == "Head_No_Helmet")
        confidence = helmet_detection["confidence"]
        explanation = "Motorcycle rider detected without a safety helmet."

    # 5. Seatbelt Violation
    has_no_seatbelt = any(d["label"] == "Driver_No_Seatbelt" for d in detections)
    if has_no_seatbelt and not has_violation:
        has_violation = True
        violation_type = "Seatbelt Violation"
        vehicle_type = "Car"
        seatbelt_detection = next(d for d in detections if d["label"] == "Driver_No_Seatbelt")
        confidence = seatbelt_detection["confidence"]
        explanation = "Driver in car detected driving without a seatbelt fastened."

    # 6. Wrong Side Driving
    for d in detections:
        if "trajectory" in d and not has_violation:
            # Trajectory moving down (wrong lane trajectory example)
            traj = d["trajectory"]
            if len(traj) >= 2:
                # If first point is higher than last point but on wrong lane, or general movement direction is reversed
                dy = traj[-1][1] - traj[0][1]
                if dy < 0: # Vehicle is driving opposite to traffic flow direction
                    has_violation = True
                    violation_type = "Wrong Side Driving"
                    vehicle_type = d["label"]
                    confidence = d["confidence"]
                    explanation = f"{d['label']} (ID {d['track_id']}) detected moving in the opposite direction of lane traffic flow."
                    break

    # 7. Illegal Parking
    has_no_parking = any(d["label"] == "No_Parking_Sign" for d in detections)
    if has_no_parking and not has_violation:
        for d in detections:
            if d["label"] in ["Car", "Motorcycle", "Auto-rickshaw", "Truck", "Bus"]:
                has_violation = True
                violation_type = "Illegal Parking"
                vehicle_type = d["label"]
                confidence = d["confidence"]
                explanation = f"{d['label']} detected stationary inside the designated No Parking zone."
                break

    # If no violation was triggered but there are vehicles, return first vehicle type
    if not has_violation:
        for d in detections:
            if d["label"] in ["Car", "Motorcycle", "Auto-rickshaw", "Truck", "Bus"]:
                vehicle_type = d["label"]
                confidence = d["confidence"]
                break

    return {
        "has_violation": has_violation,
        "violation_type": violation_type,
        "explanation": explanation,
        "confidence": confidence,
        "vehicle_type": vehicle_type if vehicle_type != "None" else "Car"
    }
