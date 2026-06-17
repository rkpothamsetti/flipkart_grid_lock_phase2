from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import base64
import uuid
import time
import os
import datetime
from PIL import Image
import io

from database import init_db, get_db, Violation, Offender, SystemLog
from pipeline.enhancement import enhance_image
from pipeline.detector import detect_objects
from pipeline.rules import check_violations
from pipeline.ocr import recognize_plate, validate_plate_format
from pipeline.evidence import generate_evidence

app = FastAPI(title="TrafficVision AI - Enforcement Platform")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure folders exist
UPLOAD_DIR = "./static/uploads"
EVIDENCE_DIR = "./static/evidence"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# Initialize database tables
init_db()

# Keep track of uploaded job file mappings in memory as a fallback
jobs_db = {}

@app.post("/api/v1/image/upload")
async def upload_image(payload: dict = Body(None), db: Session = Depends(get_db)):
    """
    POST /api/v1/image/upload
    Expects: {"camera_id": "CAM001", "image": "base64_encoded_image"}
    """
    if not payload or "image" not in payload:
        raise HTTPException(status_code=400, detail="Invalid request. Payload must contain 'image' key.")
        
    camera_id = payload.get("camera_id", "CAM001")
    image_b64 = payload["image"]
    
    # Clean up base64 prefix if present (e.g. data:image/jpeg;base64,...)
    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]
        
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode base64 image: {str(e)}")
        
    job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
    filename = f"{job_id}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    image.save(filepath, "JPEG")
    
    jobs_db[job_id] = {
        "filepath": filepath,
        "camera_id": camera_id,
        "timestamp": datetime.datetime.utcnow()
    }
    
    return {"job_id": job_id}

@app.post("/api/v1/image/upload-file")
async def upload_image_file(file: UploadFile = File(...), camera_id: str = Form("CAM001")):
    """
    Helper endpoint to accept standard multipart/form-data image uploads from the UI.
    """
    job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
    
    # Preserve filename hints for violation simulation testing (e.g. 'helmet.jpg')
    clean_filename = file.filename.replace(" ", "_")
    filepath = os.path.join(UPLOAD_DIR, f"{job_id}_{clean_filename}")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image.save(filepath, "JPEG")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
    jobs_db[job_id] = {
        "filepath": filepath,
        "camera_id": camera_id,
        "timestamp": datetime.datetime.utcnow()
    }
    
    return {"job_id": job_id}

@app.post("/api/v1/analyze")
async def analyze_image(payload: dict = Body(None), db: Session = Depends(get_db)):
    """
    POST /api/v1/analyze
    Runs the full image processing pipeline.
    """
    start_time = time.time()
    
    # Find job_id to analyze
    job_id = None
    if payload and "job_id" in payload:
        job_id = payload["job_id"]
    else:
        # Fallback to the latest uploaded job if none provided
        if jobs_db:
            job_id = list(jobs_db.keys())[-1]
            
    if not job_id or job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found or no upload history exists.")
        
    job_info = jobs_db[job_id]
    image_path = job_info["filepath"]
    camera_id = job_info["camera_id"]
    
    try:
        # 1. Load original image
        pil_image = Image.open(image_path)
        
        # 2. Image Enhancement (Zero-DCE / Restormer)
        enhanced_pil, enhancement_stats = enhance_image(pil_image)
        
        # 3. YOLO Detection & ByteTrack tracking simulation
        detection_data = detect_objects(image_path)
        detections = detection_data["detections"]
        
        # 4. Violation check using Rules engine
        violation_info = check_violations(detections)
        
        # 5. PaddleOCR plate extraction
        plate_number = recognize_plate(image_path)
        
        # 6. Generate Annotated Evidence Image
        evidence_id = f"EV_{uuid.uuid4().hex[:8].upper()}"
        evidence_filename = f"{evidence_id}.jpg"
        evidence_filepath = os.path.join(EVIDENCE_DIR, evidence_filename)
        
        generate_evidence(enhanced_pil, detections, violation_info, plate_number, evidence_filepath)
        
        # Save results in Database
        violation_db_entry = Violation(
            camera_id=camera_id,
            vehicle_type=violation_info["vehicle_type"],
            violation_type=violation_info["violation_type"],
            confidence=violation_info["confidence"],
            plate_number=plate_number,
            image_url=f"/static/uploads/{os.path.basename(image_path)}",
            annotated_image_url=f"/static/evidence/{evidence_filename}",
            explanation=violation_info["explanation"]
        )
        db.add(violation_db_entry)
        
        # Update Offender stats if it is a violation
        if violation_info["has_violation"]:
            offender = db.query(Offender).filter(Offender.plate_number == plate_number).first()
            if not offender:
                offender = Offender(plate_number=plate_number, offence_count=1)
                db.add(offender)
            else:
                offender.offence_count += 1
                offender.last_offence_timestamp = datetime.datetime.utcnow()
                
        db.commit()
        
        # Log successful run metrics
        processing_time_ms = (time.time() - start_time) * 1000
        sys_log = SystemLog(processing_time_ms=processing_time_ms, success=True)
        db.add(sys_log)
        db.commit()
        
        return {
            "vehicle_type": violation_info["vehicle_type"],
            "violation": violation_info["violation_type"],
            "confidence": round(violation_info["confidence"], 2),
            "plate_number": plate_number,
            "evidence_id": violation_db_entry.id, # DB autoincrement ID
            "image_url": violation_db_entry.image_url,
            "annotated_image_url": violation_db_entry.annotated_image_url,
            "explanation": violation_db_entry.explanation,
            "enhancement_stats": enhancement_stats
        }
        
    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        sys_log = SystemLog(processing_time_ms=processing_time_ms, success=False, error_message=str(e))
        db.add(sys_log)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/api/v1/evidence/{id}")
async def get_evidence(id: int, db: Session = Depends(get_db)):
    """
    GET /api/v1/evidence/{id}
    Retrieves evidence details.
    """
    violation = db.query(Violation).filter(Violation.id == id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Evidence with ID {id} not found.")
        
    return {
        "evidence_id": f"EV_{violation.id:03d}",
        "plate_number": violation.plate_number,
        "violation": violation.violation_type,
        "timestamp": violation.timestamp.isoformat() + "Z",
        "confidence": round(violation.confidence, 2),
        "image_url": violation.annotated_image_url,
        "original_image_url": violation.image_url,
        "vehicle_type": violation.vehicle_type,
        "explanation": violation.explanation,
        "camera_id": violation.camera_id
    }

@app.get("/api/v1/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """
    GET /api/v1/analytics
    Returns counts for different violation types, trends, and repeat offenders.
    """
    violations = db.query(Violation).all()
    
    # Base response spec counts
    counts = {
        "helmet": 0,
        "seatbelt": 0,
        "wrong_side": 0,
        "illegal_parking": 0,
        "triple_riding": 0,
        "stop_line": 0,
        "red_light": 0
    }
    
    recent_feed = []
    
    for v in violations:
        vtype = v.violation_type.lower().replace(" ", "_")
        if vtype in counts:
            counts[vtype] += 1
            
        recent_feed.append({
            "id": v.id,
            "camera_id": v.camera_id,
            "vehicle_type": v.vehicle_type,
            "violation": v.violation_type,
            "plate_number": v.plate_number,
            "confidence": round(v.confidence, 2),
            "timestamp": v.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    # Query repeat offenders
    offenders_query = db.query(Offender).filter(Offender.offence_count >= 2).order_by(Offender.offence_count.desc()).limit(10).all()
    repeat_offenders = [
        {
            "plate_number": o.plate_number,
            "offence_count": o.offence_count,
            "last_offence": o.last_offence_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for o in offenders_query
    ]
    
    # Query system health averages
    logs = db.query(SystemLog).filter(SystemLog.success == True).all()
    avg_processing_time = sum(l.processing_time_ms for l in logs) / len(logs) if logs else 0.0
    
    return {
        "helmet": counts["helmet"],
        "seatbelt": counts["seatbelt"],
        "wrong_side": counts["wrong_side"],
        "illegal_parking": counts["illegal_parking"],
        "triple_riding": counts["triple_riding"],
        "stop_line": counts["stop_line"],
        "red_light": counts["red_light"],
        "total_violations": sum(counts.values()),
        "recent_feed": sorted(recent_feed, key=lambda x: x["timestamp"], reverse=True)[:10],
        "repeat_offenders": repeat_offenders,
        "system_health": {
            "avg_latency_ms": round(avg_processing_time, 2),
            "success_rate": 100.0 if not db.query(SystemLog).all() else round((db.query(SystemLog).filter(SystemLog.success == True).count() / db.query(SystemLog).count()) * 100, 2)
        }
    }

# Mount static folder
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/")
def read_root():
    return {"message": "TrafficVision AI Backend is Running. Go to /static/index.html to view dashboard."}
