// Global state
let chart = null;

// Initialize dashboard on load
document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    fetchAnalytics();
    setupEventListeners();
});

// Setup Chart.js
function initCharts() {
    const ctx = document.getElementById('violationChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Helmet', 'Seatbelt', 'Wrong Side', 'Illegal Parking', 'Triple Riding', 'Stop Line', 'Red Light'],
            datasets: [{
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    '#8b5cf6', // Violet
                    '#06b6d4', // Cyan
                    '#f59e0b', // Amber
                    '#ef4444', // Red
                    '#ec4899', // Pink
                    '#3b82f6', // Blue
                    '#10b981'  // Emerald
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// Fetch stats and list from backend
async function fetchAnalytics() {
    try {
        const res = await fetch("/api/v1/analytics");
        if (!res.ok) throw new Error("Failed to fetch analytics");
        const data = await res.json();
        
        // Update stats
        document.getElementById("stat-helmet").innerText = data.helmet;
        document.getElementById("stat-seatbelt").innerText = data.seatbelt;
        document.getElementById("stat-wrongside").innerText = data.wrong_side;
        document.getElementById("stat-total").innerText = data.total_violations;
        
        document.getElementById("latency-val").innerText = `${data.system_health.avg_latency_ms}ms`;
        
        // Update charts
        chart.data.datasets[0].data = [
            data.helmet,
            data.seatbelt,
            data.wrong_side,
            data.illegal_parking,
            data.triple_riding,
            data.stop_line,
            data.red_light
        ];
        chart.update();
        
        // Update table logs
        const tbody = document.getElementById("violations-tbody");
        if (data.recent_feed.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No violations detected yet. Try uploading an image.</td></tr>`;
        } else {
            tbody.innerHTML = data.recent_feed.map(item => `
                <tr>
                    <td><strong>${item.camera_id}</strong></td>
                    <td>${item.timestamp}</td>
                    <td>${item.vehicle_type}</td>
                    <td><span class="badge" style="background-color: rgba(239, 68, 68, 0.15); color: #f87171;">${item.violation}</span></td>
                    <td><span class="offender-plate" style="font-size: 12px; padding: 2px 6px;">${item.plate_number}</span></td>
                    <td>${Math.round(item.confidence * 100)}%</td>
                    <td><button class="view-btn" onclick="openEvidence(${item.id})">Inspect</button></td>
                </tr>
            `).join("");
        }
        
        // Update offenders
        const offendersContainer = document.getElementById("offenders-list-container");
        if (data.repeat_offenders.length === 0) {
            offendersContainer.innerHTML = `<p class="empty-state">No repeat offenders registered yet.</p>`;
        } else {
            offendersContainer.innerHTML = data.repeat_offenders.map(off => `
                <div class="offender-item">
                    <span class="offender-plate">${off.plate_number}</span>
                    <span class="offender-count-badge">${off.offence_count} Offences</span>
                </div>
            `).join("");
        }
        
    } catch (err) {
        console.error("Error updates: ", err);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Browse File Input
    const fileUpload = document.getElementById("file-upload");
    fileUpload.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // Scenario Simulation Buttons
    const scenarioBtns = document.querySelectorAll(".btn-scenario");
    scenarioBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const type = btn.getAttribute("data-type");
            simulateScenario(type);
        });
    });
    
    // Modal controls
    document.getElementById("modal-close-btn").addEventListener("click", closeModal);
    document.getElementById("modal-close-overlay").addEventListener("click", closeModal);
    document.getElementById("modal-close-action").addEventListener("click", closeModal);
    
    // Search
    const searchInput = document.getElementById("plate-search-input");
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toUpperCase();
        filterLogs(query);
    });
}

// Upload & Analyze function
async function handleFileUpload(file, filenameHint = "") {
    const container = document.getElementById("camera-stream-container");
    container.innerHTML = `
        <div class="stream-placeholder">
            <i class="fa-solid fa-circle-notch fa-spin upload-huge-icon" style="color: #8b5cf6;"></i>
            <p>Enhancing Image, Running YOLOv11 & OCR Engine...</p>
        </div>
    `;
    
    const formData = new FormData();
    // Rename file if we have a hint to trigger specific violation
    if (filenameHint) {
        const blob = file.slice(0, file.size, file.type);
        file = new File([blob], filenameHint, {type: file.type});
    }
    formData.append("file", file);
    formData.append("camera_id", "CAM_" + Math.floor(100 + Math.random() * 900));
    
    try {
        // Step 1: Upload
        const uploadRes = await fetch("/api/v1/image/upload-file", {
            method: "POST",
            body: formData
        });
        if (!uploadRes.ok) throw new Error("Upload failed");
        const uploadData = await uploadRes.json();
        
        // Step 2: Analyze
        const analyzeRes = await fetch("/api/v1/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_id: uploadData.job_id })
        });
        if (!analyzeRes.ok) throw new Error("Analysis failed");
        const analysis = await analyzeRes.json();
        
        // Update display with annotated image
        container.innerHTML = `
            <img src="${analysis.annotated_image_url}" style="width: 100%; height: 100%; object-fit: contain;">
        `;
        
        // Refresh stats & list
        await fetchAnalytics();
        
    } catch (err) {
        alert("Pipeline processing error: " + err.message);
        resetUploadArea();
    }
}

function resetUploadArea() {
    const container = document.getElementById("camera-stream-container");
    container.innerHTML = `
        <div class="stream-placeholder">
            <i class="fa-cloud-arrow-up upload-huge-icon"></i>
            <p>Drag & drop or select an image to process</p>
            <label class="upload-btn">
                <input type="file" id="file-upload" accept="image/*" style="display: none;">
                Browse Image
            </label>
        </div>
    `;
    // Rebind input listener
    document.getElementById("file-upload").addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// Generate dynamic images on canvas to simulate scenarios instantly without needing assets
function simulateScenario(type) {
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    
    // Draw some roads and background
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, 0, 640, 480);
    
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 10;
    ctx.beginPath();
    ctx.moveTo(320, 0);
    ctx.lineTo(320, 480);
    ctx.stroke();
    
    // Draw scenario text in the canvas mock background so it's readable
    ctx.fillStyle = "#94a3b8";
    ctx.font = "24px Outfit";
    ctx.fillText(`Simulated Live Traffic - ${type.toUpperCase()}`, 50, 240);
    
    canvas.toBlob((blob) => {
        const file = new File([blob], `${type}.jpg`, {type: "image/jpeg"});
        handleFileUpload(file, `${type}.jpg`);
    }, "image/jpeg");
}

// Open Evidence dossier modal
async function openEvidence(id) {
    try {
        const res = await fetch(`/api/v1/evidence/${id}`);
        if (!res.ok) throw new Error("Failed to get evidence details");
        const data = await res.json();
        
        document.getElementById("modal-original-img").src = data.original_image_url;
        document.getElementById("modal-annotated-img").src = data.image_url;
        document.getElementById("modal-plate").innerText = data.plate_number;
        document.getElementById("modal-violation").innerText = data.violation;
        document.getElementById("modal-confidence").innerText = `${Math.round(data.confidence * 100)}%`;
        document.getElementById("modal-timestamp").innerText = data.timestamp;
        document.getElementById("modal-explanation").innerText = data.explanation;
        
        document.getElementById("evidence-modal").classList.add("active");
    } catch (err) {
        alert("Could not load evidence: " + err.message);
    }
}

function closeModal() {
    document.getElementById("evidence-modal").classList.remove("active");
}

// Client-side search filtering
function filterLogs(query) {
    const rows = document.querySelectorAll("#violations-tbody tr");
    rows.forEach(row => {
        const plateCell = row.querySelector(".offender-plate");
        if (plateCell) {
            const plateText = plateCell.innerText;
            if (plateText.includes(query)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }
    });
}
