# TrafficVision AI - Enforcement Platform

TrafficVision AI is a high-fidelity simulated traffic enforcement platform designed to detect, track, and record traffic violations in real-time. The system processes traffic camera feeds, applies enhancement techniques for low-light/noisy conditions, detects vehicles and road users, evaluates local traffic rules (helmet compliance, stop line boundaries, wrong-side driving, triple riding, etc.), extracts license plates using OCR, and stores logs and repeat offender data in a centralized database with a premium frontend dashboard for operators.

---

## 🚀 Key Features

*   **Adaptive Image Quality Check & Restoration**: Simulates **Zero-DCE** (low-light correction) and **Restormer** (denoising/deblurring) algorithms.
*   **Object Detection & Tracking**: Simulates **YOLOv11** (vehicle, pedestrian, rider detection) and **ByteTrack** (vehicle identity tracking and movement trajectory).
*   **Logical Rule Engine**: Flags critical traffic violations:
    1.  **Helmet Violations** (Two-wheeler riders without helmets)
    2.  **Seatbelt Violations** (Four-wheeler drivers without seatbelts)
    3.  **Triple Riding** (Motorcycles carrying 3 or more riders)
    4.  **Wrong-Side Driving** (Vehicles driving opposite to lane direction)
    5.  **Stop-Line Crossing** (Vehicles crossing the line during a red light)
    6.  **Red-Light Violations** (Vehicles crossing the junction boundary on red)
    7.  **Illegal Parking** (Vehicles stationary in no-parking zones)
*   **License Plate Recognition (OCR)**: Simulates character extraction using **PaddleOCR** with standard format validation.
*   **Evidence Dossier Generation**: Creates annotated evidence images featuring bounding boxes, warning colors, and overlay headers.
*   **Interactive Dashboard**: Dark-mode operator interface with statistics, charts, live log feeds, and repeat offender intelligence.
*   **System Reliability Logging**: Logs transaction latencies, success rates, and errors.

---

## 📂 Project Structure

```
├── main.py              # FastAPI server, REST API endpoints, routing
├── database.py          # SQLite database connection and SQLAlchemy models
├── requirements.txt     # Python dependency list
├── walkthrough.md       # Platform design and setup summary
├── pipeline/            # Simulation pipeline modules
│   ├── enhancement.py   # Low-light & deblur simulation (Zero-DCE, Restormer)
│   ├── detector.py      # Bounding box & class detection (YOLOv11, ByteTrack)
│   ├── rules.py         # Logical rule evaluation for traffic violations
│   ├── ocr.py           # License plate recognition & verification (PaddleOCR)
│   └── evidence.py      # Bounding box annotation and evidence JPEG builder
├── static/              # Dashboard UI files
│   ├── index.html       # HTML layout structure
│   ├── style.css        # Premium glassmorphic stylesheet
│   └── app.js           # Client-side API request handler & chart renderer
├── tests/
│   └── test_pipeline.py # Unit tests for the pipeline engine
└── traffic_vision.db    # SQLite database file (auto-generated)
```

---

## 🛠️ Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Install Dependencies
Install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Running the Server
Start the FastAPI backend server using `uvicorn`:
```bash
uvicorn main:app --reload
```
Once started, the backend API will run on `http://127.0.0.1:8000`.

### 4. Viewing the Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:8000/static/index.html
```

---

## 📊 API Reference

### 1. Upload Image
*   **Endpoint**: `POST /api/v1/image/upload`
*   **Payload**:
    ```json
    {
      "camera_id": "CAM001",
      "image": "base64_encoded_image_string"
    }
    ```
*   **Response**:
    ```json
    {
      "job_id": "JOB_A1B2C3D4"
    }
    ```

### 2. Run Pipeline Analysis
*   **Endpoint**: `POST /api/v1/analyze`
*   **Payload** (Optional):
    ```json
    {
      "job_id": "JOB_A1B2C3D4"
    }
    ```
*   **Response**: Returns details of the violation type, plate number, confidence, and paths to both original and annotated evidence images.

### 3. Retrieve Evidence
*   **Endpoint**: `GET /api/v1/evidence/{id}`
*   **Response**: Detail dossier containing camera metadata, confidence score, and challan explanation.

### 4. Retrieve Analytics
*   **Endpoint**: `GET /api/v1/analytics`
*   **Response**: Aggregated counts for violation categories, a list of repeat offenders, and latency/success rate health stats.

---

## 🧪 Running Unit Tests

Run the pipeline verification test suite with the following command:
```bash
python -m unittest tests/test_pipeline.py
```
