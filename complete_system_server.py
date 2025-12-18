#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - COMPLETE SYSTEM SERVER
Menggabungkan semua komponen sistem dalam satu server dengan live dashboard
"""

import asyncio
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Setup path
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Buat direktori yang diperlukan
for directory in [UPLOADS_DIR, RESULTS_DIR, LOGS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Setup FastAPI
app = FastAPI(
    title="Cyber Crack Pro v3.0 - Complete System Server",
    description="All-in-One server with live dashboard for APK modification system",
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
        self.bot_messages = ["System started"]
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
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass  # Jika koneksi putus, abaikan

manager = ConnectionManager()

@app.get("/")
async def root():
    """Root dashboard untuk mengakses semua fitur sistem"""
    return templates.TemplateResponse("index.html", {"request": None})

@app.get("/dashboard")
async def dashboard():
    """Live dashboard untuk semua komponen sistem"""
    return templates.TemplateResponse("dashboard.html", {"request": None})

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
            await manager.broadcast(global_state.to_dict())
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

# Simulasikan bot berjalan dan mengirim pesan ke sistem
async def bot_simulator():
    """Simulasi bot telegram yang mengirim pesan ke sistem"""
    global global_state

    while True:
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
                "job": job_dict,
                "message": f"Memproses: {job.original_apk}"
            })

            try:
                # Simulasikan langkah-langkah proses dengan penanganan timeout
                # Dalam sistem Analysis-Before-Execution, ada dua fase utama: analysis dan execution
                phases = [
                    ("Analysis", [
                        "Mengekstrak APK...",
                        "Menganalisis struktur...",
                        "Mendeteksi keamanan...",
                        "Mapping fitur premium..."
                    ]),
                    ("Execution", [
                        "Menerapkan modifikasi...",
                        "Membangun ulang APK...",
                        "Menandatangani file...",
                        "Verifikasi selesai..."
                    ])
                ]

                total_phases = len(phases)
                for phase_idx, (phase_name, steps) in enumerate(phases):
                    for step_idx, step in enumerate(steps):
                        # Calculate progress: 40% for analysis, 60% for execution
                        if phase_name == "Analysis":
                            job.progress = int(10 + (step_idx + 1) / len(steps) * 30)  # 10% to 40%
                        else:  # Execution
                            job.progress = int(40 + (step_idx + 1) / len(steps) * 60)  # 40% to 100%

                        # Kirim update
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
                            "type": "process_step",
                            "step": step,
                            "job": job_dict,
                            "progress": job.progress,
                            "phase": phase_name
                        })

                        # Tambahkan penanganan timeout untuk mencegah proses macet
                        await asyncio.wait_for(asyncio.sleep(3), timeout=15)  # Timeout 15 detik per langkah

            except asyncio.TimeoutError:
                # Jika terjadi timeout, tandai sebagai error dan lanjutkan ke proses berikutnya
                job.status = "timeout_error"
                job.progress = 100
                await manager.broadcast({
                    "type": "process_error",
                    "job": job_dict,
                    "message": f"Timeout saat memproses: {job.original_apk}"
                })
            except Exception as e:
                # Jika terjadi error lain, tandai sebagai error dan lanjutkan
                job.status = "error"
                job.progress = 100
                await manager.broadcast({
                    "type": "process_error",
                    "job": job_dict,
                    "message": f"Error saat memproses: {job.original_apk} - {str(e)}"
                })
            finally:
                # Pastikan untuk membersihkan state proses saat ini
                if global_state.current_process == job:
                    global_state.completed_jobs.append(job)
                    global_state.current_process = None
                    if job.status in ["completed", "timeout_error", "error"]:
                        global_state.system_stats["total_processed"] += 1
                        if job.status == "completed":
                            global_state.system_stats["successful_runs"] += 1
                        else:
                            global_state.system_stats["failed_runs"] += 1

                # Kirim update selesai
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
                    "type": "process_complete",
                    "job": job_dict,
                    "message": f"Proses selesai: {job.original_apk} (Status: {job.status})"
                })
        else:
            # Jika tidak ada proses, tunggu sebentar sebelum cek lagi
            await asyncio.sleep(5)

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
            "stats": global_state.system_stats
        })

# Buat template HTML untuk dashboard
def create_templates_if_not_exists():
    """Buat template HTML jika belum ada"""
    
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
                
                document.getElementById('currentProcessStatus').innerHTML = 
                    `<p><strong>Step:</strong> ${data.step}</p>` +
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
            else {
                // Update counters for general status changes
                if (data.system_stats) {
                    document.getElementById('completedCount').textContent = data.system_stats.total_processed;
                    document.getElementById('uptime').textContent = data.system_stats.uptime;
                }
                
                if (data.bot_messages) {
                    const messagesDiv = document.getElementById('botMessages');
                    messagesDiv.innerHTML = '';
                    
                    // Show last 10 messages
                    const messagesToShow = data.bot_messages.slice(-10);
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
        };
        
        ws.onerror = function(error) {
            console.log('WebSocket error: ', error);
        };
        
        // Fetch initial status
        async function fetchInitialStatus() {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            document.getElementById('completedCount').textContent = status.total_completed;
            document.getElementById('queueCount').textContent = status.process_queue_length;
            document.getElementById('uptime').textContent = status.system_uptime;
            document.getElementById('activeUsers').textContent = status.active_users;
        }
        
        fetchInitialStatus();
    </script>
</body>
</html>
"""
    
    if not (TEMPLATES_DIR / "index.html").exists():
        with open(TEMPLATES_DIR / "index.html", 'w') as f:
            f.write(index_html)
    
    if not (TEMPLATES_DIR / "dashboard.html").exists():
        with open(TEMPLATES_DIR / "dashboard.html", 'w') as f:
            f.write(index_html)

# Function to run the server
async def run_server():
    """Run the complete system server"""
    print("🚀 Starting Cyber Crack Pro v3.0 - Complete System Server")
    print("📋 Features available:")
    print("   • Live dashboard at: http://localhost:8000")
    print("   • WebSocket for real-time updates")
    print("   • API endpoints for system control")
    print("   • Process queue monitoring")
    print("   • Bot message visualization")
    print("   • Two-step Analysis-Before-Execution process")
    print("   • Real-time system resource monitoring")
    print()
    print("🔗 System components now unified in single server")

    # Create templates
    create_templates_if_not_exists()

    # Start simulator tasks
    asyncio.create_task(bot_simulator())
    asyncio.create_task(analysis_execution_simulator())

    # Run server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # Jalankan server
    import sys
    import os
    sys.path.append(str(BASE_DIR))

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()