#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - WEB PLATFORM SYSTEM
Sistem utama web platform dengan Analysis-Before-Execution dan penanganan error yang diperbaiki
"""

import asyncio
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Setup path dan direktori
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Setup logging untuk mencocokkan format log dari sistem asli
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Buat direktori yang diperlukan
for directory in [UPLOADS_DIR, RESULTS_DIR, LOGS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Setup FastAPI
app = FastAPI(
    title="Cyber Crack Pro v3.0 - Web Platform System",
    description="Web platform dengan Analysis-Before-Execution dan penanganan error yang diperbaiki",
    version="3.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Global state untuk menyimpan status sistem secara real-time
class GlobalSystemState:
    def __init__(self):
        self.bot_status = "active"
        self.backend_status = "running"
        self.process_queue = []
        self.completed_jobs = []
        self.current_process = None
        self.bot_messages = []
        self.system_stats = {
            "active_users": 0,
            "total_processed": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "uptime": "00:00:00"
        }
        self.start_time = time.time()
        self.active_connections = []

    def to_dict(self):
        """Konversi state ke dictionary untuk websocket/json"""
        return {
            "bot_status": self.bot_status,
            "backend_status": self.backend_status,
            "process_queue": self.process_queue,
            "completed_jobs": self.completed_jobs,
            "current_process": self.current_process.__dict__ if self.current_process else None,
            "bot_messages": self.bot_messages,
            "system_stats": self.system_stats,
            "start_time": self.start_time
        }

global_state = GlobalSystemState()

# Models
class ProcessJob(BaseModel):
    id: str
    original_apk: str
    status: str
    operation_type: str
    user_id: int
    timestamp: str
    progress: int = 0
    estimated_completion: str = "Calculating..."

class SystemStatus(BaseModel):
    bot_status: str
    backend_status: str
    process_queue_length: int
    active_processes: int
    total_completed: int
    system_uptime: str
    active_users: int
    stats: Dict

# Websocket untuk live updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)  # Tandai koneksi yang putus
                
        # Hapus koneksi yang putus
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.get("/")
async def root(request: Request):
    """Root dashboard untuk mengakses semua fitur sistem"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """Live dashboard untuk semua komponen sistem"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "request": request})

@app.get("/api/status")
async def get_status():
    """API untuk mendapatkan status sistem secara real-time"""
    global global_state

    uptime_seconds = time.time() - global_state.start_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    global_state.system_stats["uptime"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    status = SystemStatus(
        bot_status=global_state.bot_status,
        backend_status=global_state.backend_status,
        process_queue_length=len(global_state.process_queue),
        active_processes=1 if global_state.current_process else 0,
        total_completed=len(global_state.completed_jobs),
        system_uptime=global_state.system_stats["uptime"],
        active_users=global_state.system_stats["active_users"],
        stats=global_state.system_stats
    )

    return status

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket untuk live updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Kirim update status sistem secara berkala
            await asyncio.sleep(1)
            await manager.broadcast({
                "type": "system_status",
                "timestamp": datetime.now().strftime("%H.%M.%S"),
                "data": global_state.to_dict()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/process")
async def submit_process(job: ProcessJob):
    """Endpoint untuk submit proses baru"""
    global global_state

    # Tambahkan ke antrian
    global_state.process_queue.append(job)

    # Kirim notifikasi ke websocket
    job_dict = job.dict() if hasattr(job, 'dict') else {
        'id': getattr(job, 'id', ''),
        'original_apk': getattr(job, 'original_apk', ''),
        'status': getattr(job, 'status', ''),
        'operation_type': getattr(job, 'operation_type', ''),
        'user_id': getattr(job, 'user_id', 0),
        'timestamp': getattr(job, 'timestamp', ''),
        'progress': getattr(job, 'progress', 0),
        'estimated_completion': getattr(job, 'estimated_completion', '')
    }

    await manager.broadcast({
        "type": "new_process",
        "timestamp": datetime.now().strftime("%H.%M.%S"),
        "job": job_dict
    })

    return {"success": True, "job_id": job.id}

@app.get("/api/processes/queue")
async def get_process_queue():
    """Dapatkan antrian proses"""
    return global_state.process_queue

@app.get("/api/processes/completed")
async def get_completed_processes():
    """Dapatkan proses yang telah selesai"""
    return global_state.completed_jobs

@app.get("/api/messages")
async def get_bot_messages():
    """Dapatkan pesan-pesan dari bot"""
    return {"messages": global_state.bot_messages}

# Fungsi untuk mencetak log dengan format seperti di sistem asli
def print_formatted_log(message: str, status: str = "ℹ️", progress: str = None):
    """Cetak log dengan format seperti sistem asli"""
    timestamp = datetime.now().strftime("%H.%M.%S")
    
    if progress:
        print(f"[{timestamp}] {status} 📈 Progress: {progress}")
    else:
        print(f"[{timestamp}] {status} {message}")

# Simulasikan bot berjalan dan mengirim pesan ke sistem
async def bot_simulator():
    """Simulasi bot telegram yang mengirim pesan ke sistem"""
    global global_state

    # Tampilkan pesan inisialisasi seperti di sistem asli
    print_formatted_log("System initialized...")
    print_formatted_log("Ready to process Android packages", "ℹ️")
    print_formatted_log("Select Android package to begin", "ℹ️")
    
    while True:
        await asyncio.sleep(5)  # Kirim update setiap 5 detik

        # Cek jika ada proses baru di antrian
        if global_state.process_queue:
            # Ambil proses pertama
            job = global_state.process_queue.pop(0)

            # Simulasikan proses
            global_state.current_process = job
            job.status = "processing"

            # Kirim update ke websocket
            job_dict = {
                'id': job.id,
                'original_apk': job.original_apk,
                'status': job.status,
                'operation_type': job.operation_type,
                'user_id': job.user_id,
                'timestamp': job.timestamp,
                'progress': job.progress,
                'estimated_completion': job.estimated_completion
            }

            await manager.broadcast({
                "type": "process_update",
                "timestamp": datetime.now().strftime("%H.%M.%S"),
                "job": job_dict,
                "message": f"Memproses: {job.original_apk}"
            })

            # Dalam sistem Analysis-Before-Execution, ada dua fase utama: analysis dan execution
            # Fase 1: Analysis
            print_formatted_log(f"Starting deep analysis...", "ℹ️")
            await asyncio.sleep(1)  # Tambah delay sebelum mulai analisis
            print_formatted_log("Analysis started", "✅")
            print_formatted_log("Checking for security measures...", "ℹ️")
            
            # Simulasikan proses analysis
            analysis_steps = [
                "Mengekstrak APK...",
                "Menganalisis struktur...",
                "Mendeteksi keamanan...",
                "Mapping fitur premium..."
            ]

            total_analysis_steps = len(analysis_steps)
            for i, step in enumerate(analysis_steps):
                job.progress = int(10 + (i + 1) / total_analysis_steps * 30)  # 10% to 40%

                # Kirim update
                print_formatted_log(f"Progress: {job.progress}% - analyzing", "ℹ️")

                await manager.broadcast({
                    "type": "process_step",
                    "step": step,
                    "job": job_dict,
                    "progress": job.progress,
                    "phase": "Analysis",
                    "timestamp": datetime.now().strftime("%H.%M.%S")
                })

                await asyncio.sleep(3)  # Tambahkan delay untuk membuatnya lebih realistis

            print_formatted_log("Analysis complete! Ready for cracking", "✅")
            await asyncio.sleep(1)  # Tambah delay sebelum mulai cracking

            # Fase 2: Execution
            await asyncio.sleep(1)  # Tambah delay sebelum memulai cracking
            print_formatted_log("Starting cracking process...", "⚠️", "50% - cracking")
            print_formatted_log("Cracking engine started", "✅")
            print_formatted_log("Applying patches...", "ℹ️")
            
            # Simulasikan proses execution
            execution_steps = [
                "Menerapkan modifikasi...",
                "Membangun ulang APK...",
                "Menandatangani file...",
                "Verifikasi selesai..."
            ]

            total_execution_steps = len(execution_steps)
            for i, step in enumerate(execution_steps):
                job.progress = int(40 + (i + 1) / total_execution_steps * 60)  # 40% to 100%

                # Kirim update
                progress_status = "cracking" if job.progress < 90 else "completed"
                print_formatted_log(f"Progress: {job.progress}% - {progress_status}", "ℹ️")

                await manager.broadcast({
                    "type": "process_step",
                    "step": step,
                    "job": job_dict,
                    "progress": job.progress,
                    "phase": "Execution",
                    "timestamp": datetime.now().strftime("%H.%M.%S")
                })

                await asyncio.sleep(4)  # Tambahkan delay untuk membuatnya lebih realistis

            # Proses selesai
            job.status = "completed"
            job.progress = 100

            global_state.completed_jobs.append(job)
            global_state.current_process = None
            global_state.system_stats["total_processed"] += 1
            global_state.system_stats["successful_runs"] += 1  # Simulasikan semua sukses

            print_formatted_log(f"Process completed: {job.original_apk}", "✅")

            # Kirim update selesai
            await manager.broadcast({
                "type": "process_complete",
                "timestamp": datetime.now().strftime("%H.%M.%S"),
                "job": job_dict,
                "message": f"Proses selesai: {job.original_apk}"
            })

            # Tambah delay sebelum melanjutkan ke proses berikutnya
            await asyncio.sleep(2)

# Simulasikan analisis dan eksekusi yang sebenarnya
async def analysis_execution_simulator():
    """Simulasi sistem Analysis-Before-Execution berjalan"""
    global global_state

    while True:
        await asyncio.sleep(10)  # Update statistik setiap 10 detik

        # Simulasikan beberapa proses yang sedang aktif
        import random

        # Update statistik sistem
        global_state.system_stats["cpu_usage"] = random.randint(10, 45)
        global_state.system_stats["memory_usage"] = random.randint(20, 60)
        global_state.system_stats["active_users"] = random.randint(1, 5)

        # Kirim update
        await manager.broadcast({
            "type": "system_update",
            "timestamp": datetime.now().strftime("%H.%M.%S"),
            "stats": global_state.system_stats
        })

def create_templates_if_not_exists():
    """Buat template HTML jika belum ada"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Index template
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Crack Pro v3.0 - System Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .card {
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
            margin-bottom: 1.5rem;
        }
        .status-indicator {
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }
        .status-active {
            background-color: #28a745;
        }
        .status-inactive {
            background-color: #dc3545;
        }
        .metric-card {
            border-left: 0.25rem solid #4e73df;
        }
        .success-card {
            border-left: 0.25rem solid #28a745;
        }
        .warning-card {
            border-left: 0.25rem solid #ffc107;
        }
        .danger-card {
            border-left: 0.25rem solid #dc3545;
        }
        #botMessages {
            max-height: 300px;
            overflow-y: auto;
        }
        .process-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
    </style>
</head>
<body id="page-top">
    <div id="wrapper">
        <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
            <h1 class="h3 mb-0 text-gray-800"><i class="fas fa-shield-alt me-2"></i>Cyber Crack Pro v3.0 - System Dashboard</h1>
        </nav>

        <div class="container-fluid">
            <!-- System Status Cards -->
            <div class="row">
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card metric-card">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                        Bot Status</div>
                                    <div class="row no-gutters align-items-center">
                                        <div class="col-auto">
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">
                                                <span class="status-indicator status-active"></span>
                                                Active
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-robot fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card success-card">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                        Completed Processes</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800" id="completedCount">0</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card warning-card">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                        Queue Length</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800" id="queueCount">0</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-list fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card danger-card">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">
                                        System Uptime</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800" id="uptime">00:00:00</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-clock fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Real-time status updates -->
            <div class="row">
                <div class="col-lg-8">
                    <div class="card shadow mb-4">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">Real-Time Process Status</h6>
                        </div>
                        <div class="card-body">
                            <div class="progress mb-4">
                                <div class="progress-bar" id="overallProgress" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                            <div id="currentProcessStatus">
                                <p>No active process</p>
                            </div>
                            <div id="processQueue">
                                <h5>Process Queue:</h5>
                                <div id="queueList"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="card shadow mb-4">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">System Resources</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <span class="small">CPU Usage</span>
                                <div class="progress mb-2">
                                    <div id="cpuProgress" class="progress-bar bg-info" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="small" id="cpuPercent">0%</span>
                            </div>

                            <div class="mb-3">
                                <span class="small">Memory Usage</span>
                                <div class="progress mb-2">
                                    <div id="memoryProgress" class="progress-bar bg-warning" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="small" id="memoryPercent">0%</span>
                            </div>

                            <div class="mb-3">
                                <h5 class="small">Active Users</h5>
                                <p id="activeUsers" class="h4">0</p>
                            </div>

                            <div class="mb-3">
                                <h5 class="small">Backend Status</h5>
                                <span class="status-indicator status-active"></span>
                                <span id="backendStatus">Running</span>
                            </div>
                        </div>
                    </div>

                    <div class="card shadow mb-4">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">Bot Messages</h6>
                        </div>
                        <div class="card-body">
                            <div id="botMessages">
                                <p>Loading messages...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Use WebSocket with the same port as our Python app
        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Received data:', data);

            if (data.type === 'system_update') {
                // Update system stats
                document.getElementById('cpuPercent').textContent = data.stats.cpu_usage + '%';
                document.getElementById('cpuProgress').style.width = data.stats.cpu_usage + '%';
                document.getElementById('cpuProgress').ariaValueNow = data.stats.cpu_usage;

                document.getElementById('memoryPercent').textContent = data.stats.memory_usage + '%';
                document.getElementById('memoryProgress').style.width = data.stats.memory_usage + '%';
                document.getElementById('memoryProgress').ariaValueNow = data.stats.memory_usage;

                document.getElementById('activeUsers').textContent = data.stats.active_users;
                document.getElementById('uptime').textContent = data.stats.uptime;
            }
            else if (data.type === 'process_update') {
                // Update process status
                document.getElementById('currentProcessStatus').innerHTML =
                    `<p><strong>Processing:</strong> ${data.job.original_apk}</p>` +
                    `<p><strong>Type:</strong> ${data.job.operation_type}</p>`;
            }
            else if (data.type === 'process_step') {
                // Update progress
                document.getElementById('overallProgress').style.width = data.progress + '%';
                document.getElementById('overallProgress').ariaValueNow = data.progress;

                let phaseInfo = '';
                if (data.phase) {
                    phaseInfo = `<p><strong>Phase:</strong> ${data.phase}</p>`;
                }

                document.getElementById('currentProcessStatus').innerHTML =
                    `<p><strong>Step:</strong> ${data.step}</p>` +
                    phaseInfo +
                    `<p><strong>Progress:</strong> ${data.progress}%</p>`;
            }
            else if (data.type === 'process_complete') {
                // Update counter
                const completedCount = parseInt(document.getElementById('completedCount').textContent) + 1;
                document.getElementById('completedCount').textContent = completedCount;

                // Reset progress bar
                document.getElementById('overallProgress').style.width = '0%';
                document.getElementById('overallProgress').ariaValueNow = '0';

                document.getElementById('currentProcessStatus').innerHTML =
                    `<p class="text-success"><strong>COMPLETED:</strong> ${data.job.original_apk}</p>`;
            }
            else if (data.type === 'new_process') {
                // Add to queue
                const queueCount = parseInt(document.getElementById('queueCount').textContent) + 1;
                document.getElementById('queueCount').textContent = queueCount;

                const queueItem = document.createElement('div');
                queueItem.className = 'process-item';
                queueItem.innerHTML = `<strong>New job:</strong> ${data.job.original_apk} (Type: ${data.job.operation_type})`;
                document.getElementById('queueList').appendChild(queueItem);
            }
            else if (data.type === 'system_status') {
                // Update counters for general status changes
                if (data.data && data.data.system_stats) {
                    document.getElementById('completedCount').textContent = data.data.system_stats.total_processed;
                    document.getElementById('uptime').textContent = data.data.system_stats.uptime;
                }

                if (data.data && data.data.bot_messages) {
                    const messagesDiv = document.getElementById('botMessages');
                    messagesDiv.innerHTML = '';

                    // Show last 10 messages
                    const messagesToShow = data.data.bot_messages.slice(-10);
                    for (const msg of messagesToShow) {
                        const p = document.createElement('p');
                        p.className = 'small mb-1';
                        p.textContent = msg;
                        messagesDiv.appendChild(p);
                    }
                }
            }
        };

        ws.onopen = function(event) {
            console.log('WebSocket connected');
            document.getElementById('currentProcessStatus').innerHTML = '<p>✅ Connected to real-time updates</p>';
        };

        ws.onerror = function(error) {
            console.log('WebSocket error: ', error);
        };

        ws.onclose = function(event) {
            console.log('WebSocket closed');
        };

        // Fetch initial status
        async function fetchInitialStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();

                document.getElementById('completedCount').textContent = status.total_completed;
                document.getElementById('queueCount').textContent = status.process_queue_length;
                document.getElementById('uptime').textContent = status.system_uptime;
                document.getElementById('activeUsers').textContent = status.active_users;
            } catch (error) {
                console.error('Error fetching initial status:', error);
            }
        }

        fetchInitialStatus();
    </script>
</body>
</html>
"""

    index_path = templates_dir / "index.html"
    if not index_path.exists():
        with open(index_path, 'w') as f:
            f.write(index_html)

    # Dashboard template
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Crack Pro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body id="page-top">
    <div id="wrapper">
        <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
            <h1 class="h3 mb-0 text-gray-800"><i class="fas fa-chart-line me-2"></i>Cyber Crack Pro - Advanced Dashboard</h1>
        </nav>

        <div class="container-fluid">
            <div class="d-sm-flex align-items-center justify-content-between mb-4">
                <h1 class="h3 mb-0 text-gray-800">System Dashboard</h1>
            </div>

            <div class="row">
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-primary shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                        System Status</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">Operational</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-success shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                        Processed Today</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">0</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-clipboard-list fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-info shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                        Active Processes</div>
                                    <div class="row no-gutters align-items-center">
                                        <div class="col-auto">
                                            <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">0</div>
                                        </div>
                                        <div class="col">
                                            <div class="progress progress-sm mr-2">
                                                <div class="progress-bar bg-info" role="progressbar" style="width: 50%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-clipboard-list fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-warning shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                        Success Rate</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">0%</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-percentage fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-6">
                    <div class="card shadow mb-4">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">Process Queue</h6>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-bordered" id="dataTable" width="100%" cellspacing="0">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>File</th>
                                            <th>Status</th>
                                            <th>Progress</th>
                                        </tr>
                                    </thead>
                                    <tbody id="queueTableBody">
                                        <tr><td colspan="4">No active processes</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow mb-4">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">System Log</h6>
                        </div>
                        <div class="card-body" style="height: 300px; overflow-y: auto;">
                            <div id="systemLog">
                                <p>System initialized...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

    dashboard_path = templates_dir / "dashboard.html"
    if not dashboard_path.exists():
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_html)

if __name__ == "__main__":
    print("🚀 CYBER CRACK PRO v3.0 - WEB PLATFORM SYSTEM")
    print("🔧 Analysis-Before-Execution System: ACTIVE")
    print("🔄 Two-Step Process: ANALYSIS → EXECUTION")
    print("⚠️  Error 422 Resolution: ACTIVE")
    print("🚀 Starting Web Platform Server on http://localhost:8000")
    
    # Buat template jika belum ada
    create_templates_if_not_exists()
    
    # Jalankan simulasi di background
    async def run_simulations():
        await asyncio.gather(
            bot_simulator(),
            analysis_execution_simulator()
        )
    
    # Mulai simulasi di thread terpisah
    import threading
    
    def start_simulations():
        asyncio.run(run_simulations())
    
    sim_thread = threading.Thread(target=start_simulations, daemon=True)
    sim_thread.start()
    
    # Jalankan server
    uvicorn.run(app, host="0.0.0.0", port=8000)