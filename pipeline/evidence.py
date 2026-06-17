from PIL import Image, ImageDraw, ImageFont
import os

def generate_evidence(image: Image.Image, detections: list, violation_info: dict, plate_number: str, output_path: str):
    """
    Draws bounding boxes, labels, highlights violations, overlays metadata, and saves the annotated evidence.
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Try to load a clean default font
    try:
        font = ImageFont.load_default()
    except IOError:
        font = None

    # Draw detections
    for det in detections:
        box = det["box"]
        # Convert relative box coordinates if they are normalized (they are absolute in our simulated detector)
        x_min, y_min, x_max, y_max = box[0], box[1], box[2], box[3]
        
        # Clip coordinates to image boundary
        x_min = max(0, min(width - 1, x_min))
        y_min = max(0, min(height - 1, y_min))
        x_max = max(0, min(width - 1, x_max))
        y_max = max(0, min(height - 1, y_max))
        
        label = det["label"]
        conf = det["confidence"]
        
        # Color schemes: Red for violations, Yellow for warning elements, Green for normal vehicles
        if "No_Helmet" in label or "No_Seatbelt" in label or "Stop_Line" in label or "Red_Light" in label or "No_Parking" in label or label.startswith("Rider_"):
            color = (255, 0, 0) # Red
            thickness = 4
        else:
            color = (0, 255, 0) # Green
            thickness = 2
            
        # Draw bounding box rectangle
        for i in range(thickness):
            draw.rectangle([x_min + i, y_min + i, x_max - i, y_max - i], outline=color)
            
        # Label background & text
        label_text = f"{label} ({conf:.2f})"
        draw.text((x_min + 5, y_min + 5), label_text, fill=(255, 255, 255), font=font)
        
    # Draw header overlay block for the violation and plate information
    overlay_h = 75
    draw.rectangle([0, 0, width, overlay_h], fill=(0, 0, 0))
    
    violation_title = violation_info["violation_type"]
    is_violation = violation_info["has_violation"]
    status_text = f"VIOLATION: {violation_title}" if is_violation else "STATUS: COMPLIANT"
    status_color = (255, 50, 50) if is_violation else (50, 255, 50)
    
    # Text headers
    draw.text((20, 15), status_text, fill=status_color, font=font)
    draw.text((20, 45), f"VEHICLE: {violation_info['vehicle_type']} | PLATE: {plate_number}", fill=(255, 255, 255), font=font)
    
    explanation = violation_info["explanation"]
    # Wrap text if long
    if len(explanation) > 60:
        explanation = explanation[:60] + "..."
    draw.text((width - 450, 30), f"Explanation: {explanation}", fill=(220, 220, 220), font=font)
    
    # Save annotated image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path, "JPEG")
    return output_path
