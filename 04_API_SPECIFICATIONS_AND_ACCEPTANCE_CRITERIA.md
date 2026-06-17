# TrafficVision AI - API Specifications

# Upload Image

## Endpoint

POST /api/v1/image/upload

## Request

{
  "camera_id": "CAM001",
  "image": "base64_encoded_image"
}

## Response

{
  "job_id": "JOB123"
}

---

# Analyze Image

## Endpoint

POST /api/v1/analyze

## Response

{
  "vehicle_type": "Motorcycle",
  "violation": "Helmet Violation",
  "confidence": 0.97,
  "plate_number": "AP09AB1234"
}

---

# Retrieve Evidence

## Endpoint

GET /api/v1/evidence/{id}

## Response

{
  "evidence_id": "EV001",
  "plate_number": "AP09AB1234",
  "violation": "Helmet Violation",
  "timestamp": "2026-06-16T09:12:00Z",
  "confidence": 0.97,
  "image_url": "/evidence/EV001.jpg"
}

---

# Violation Analytics

## Endpoint

GET /api/v1/analytics

## Response

{
  "helmet": 2312,
  "seatbelt": 982,
  "wrong_side": 413,
  "illegal_parking": 120
}

---

# Acceptance Criteria

## Helmet Detection

Precision >= 90%

Recall >= 90%

---

## Seatbelt Detection

Precision >= 85%

Recall >= 85%

---

## Triple Riding

F1 Score >= 90%

---

## Wrong Side Detection

F1 Score >= 90%

---

## OCR

Plate Recognition Accuracy >= 92%

---

## Stop Line Violation

Precision >= 90%

Recall >= 90%

---

## Red Light Violation

Precision >= 90%

Recall >= 90%

---

## Illegal Parking

Precision >= 90%

Recall >= 90%

---

## Processing Performance

Image Processing Time < 2 seconds

---

## Dashboard Requirements

Dashboard shall provide:

- Violation statistics
- Hotspot visualization
- Search by plate number
- Repeat offender reports

---

## System Reliability

System availability >= 99%

---

# Success Criteria

The platform is considered successful if:

- Automated detection reduces manual review effort by at least 70%.
- Violation detection accuracy exceeds 90%.
- OCR accuracy exceeds 92%.
- End-to-end processing remains below 2 seconds per image.
- Dashboard provides actionable enforcement insights.