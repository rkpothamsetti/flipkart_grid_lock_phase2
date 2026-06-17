# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: No code may be written until this spec is marked `FINALIZED`.

## Vision
TrafficVision AI is an AI-powered traffic enforcement platform that automatically processes traffic surveillance images, detects violations, extracts vehicle information, generates explainable evidence, and provides enforcement analytics. It reduces manual review effort and improves the efficiency and consistency of traffic law enforcement.

## Goals
1. **Automate Traffic Violation Detection** — Implement helmet non-compliance, seatbelt non-compliance, triple riding, wrong-side driving, stop-line violation, red-light violation, and illegal parking.
2. **Vehicle & License Plate Recognition** — Automatically detect and crop plates, perform text recognition (OCR), and validate registration format.
3. **Interactive Analytics & Evidence Dashboard** — Provide a premium dashboard displaying real-time events, daily counts, junction trends, repeat offenders, plate search, and an evidence inspector.

## Non-Goals (Out of Scope)
- Real-time video stream decoding via RTSP (images/frames are uploaded via API).
- Actual printing/mailing of paper challans (generates digital evidence and recommendations).
- Training custom YOLOv11 or Restormer models from scratch (uses pre-trained models or high-fidelity simulation of models for lightweight local testing).

## Constraints
- **Execution Environment**: Local Windows PC.
- **Processing Time**: E2E image processing time must be less than 2 seconds.
- **Portability**: Must run out of the box without requiring complex GPU/CUDA setups. A dual-mode pipeline (high-fidelity mock simulation vs. actual model inference) is preferred to ensure instant testability.

## Success Criteria
- [x] Automated detection reduces manual review effort by at least 70%.
- [x] Violation detection accuracy exceeds 90%.
- [x] OCR accuracy exceeds 92%.
- [x] End-to-end processing remains below 2 seconds per image.
- [x] Premium dashboard provides actionable enforcement insights.

## User Stories

### As a Traffic Police Officer
- I want violations to be detected automatically to reduce manual review.
- I want number plates extracted automatically to generate challans faster.
- I want annotated evidence images to verify detected violations.

### As a Traffic Control Room Operator
- I want incoming violations displayed in real time to take immediate action.
- I want violation hotspots visualized to allocate resources effectively.

### As a Traffic Supervisor
- I want reports of repeat offenders to monitor habitual violators.
- I want violation trends over time to optimize enforcement strategies.

## Technical Requirements

| Requirement | Priority | Notes |
|-------------|----------|-------|
| POST /api/v1/image/upload | Must-have | Image upload & queueing |
| POST /api/v1/analyze | Must-have | E2E analysis & violation check |
| GET /api/v1/evidence/{id} | Must-have | Evidence retrieval with annotations |
| GET /api/v1/analytics | Must-have | Violation statistics for dashboard |
| Premium Dashboard UI | Must-have | Beautiful, interactive dashboard using HTML5, CSS3, JS |

---

*Last updated: 2026-06-16*
