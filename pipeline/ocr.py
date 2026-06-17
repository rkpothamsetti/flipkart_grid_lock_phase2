import random
import re

# Standard states and some plate formats
STATES = ["MH", "DL", "KA", "AP", "TS", "UP", "HR", "TN", "KA", "GJ"]

def recognize_plate(image_path: str) -> str:
    """
    Simulates license plate extraction and text character recognition (PaddleOCR).
    Returns a validated license plate string.
    """
    # Deterministic check based on filename if provided, else random
    import os
    filename = os.path.basename(image_path).lower()
    
    # Check for hardcoded tags in filename
    plate_match = re.search(r"([a-z]{2}\d{2}[a-z]{2}\d{4})", filename)
    if plate_match:
        return plate_match.group(1).upper()
        
    if "helmet" in filename:
        return "MH12HN9823"
    elif "seatbelt" in filename:
        return "DL3CAF5521"
    elif "triple" in filename:
        return "KA03TR3319"
    elif "wrong" in filename:
        return "TS09WS4120"
    elif "stopline" in filename:
        return "AP10SL7781"
    elif "redlight" in filename:
        return "UP16RL8890"
    elif "parking" in filename:
        return "HR26IP2212"
        
    # Standard format: State(2 letters) + District(2 digits) + Series(2 letters) + Number(4 digits)
    state = random.choice(STATES)
    district = f"{random.randint(1, 99):02d}"
    series = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
    num = f"{random.randint(1, 9999):04d}"
    
    return f"{state}{district}{series}{num}"

def validate_plate_format(plate: str) -> bool:
    """
    Validates standard Indian/international format.
    Regex validates format like: MH12AB1234 or DL3CAF5521
    """
    pattern = r"^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}$"
    return bool(re.match(pattern, plate))
