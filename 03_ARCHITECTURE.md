# TrafficVision AI - Architecture Document

# High-Level Architecture

┌─────────────────────┐
│ Traffic Cameras     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Image Quality Check │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Enhancement Layer   │
│ Zero-DCE            │
│ Restormer           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ YOLO Detection      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ByteTrack Tracking  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Rule Engine         │
│ Violation Analysis  │
└──────┬──────┬───────┘
       │      │
       ▼      ▼
 OCR Engine  Analytics
       │
       ▼
 Evidence Generator

---

# Component Details

## Image Enhancement Layer

Repositories:

- Zero-DCE
- Restormer

Responsibilities:

- Low-light correction
- Deblurring
- Denoising

---

## Detection Layer

Repository:

- YOLOv11

Responsibilities:

- Vehicle detection
- Rider detection
- Pedestrian detection

---

## Tracking Layer

Repository:

- ByteTrack

Responsibilities:

- Vehicle identity tracking
- Trajectory generation

---

## Violation Reasoning Layer

Responsibilities:

- Helmet detection
- Seatbelt detection
- Triple riding
- Wrong-side driving
- Stop-line crossing
- Red-light violation
- Illegal parking

---

## OCR Layer

Repository:

- PaddleOCR

Responsibilities:

- Plate extraction
- Text recognition

---

## Evidence Layer

Responsibilities:

- Annotated image creation
- Timestamp association
- Confidence explanation

---

## Analytics Layer

Responsibilities:

- Trend analysis
- Heatmaps
- Repeat offender tracking

---

# Data Flow

Camera Image
→ Enhancement
→ Detection
→ Tracking
→ Violation Engine
→ OCR
→ Evidence Generation
→ Database
→ Dashboard