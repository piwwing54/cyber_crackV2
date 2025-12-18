#!/usr/bin/env python3
"""
📊 CYBER CRACK PRO v3.0 - WEB DASHBOARD
Dashboard untuk memantau sistem bot Telegram dan proses analisis
"""

import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
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
app = FastAPI(title="Cyber Crack Pro v3.0 - Web Dashboard", version="3.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Models
class SystemStatus(BaseModel):
    bot_running: bool
    total_processes: int
    successful_processes: int
    failed_processes: int
    uptime: str
    cpu_usage: float
    memory_usage: float
    active_users: int

class ProcessInfo(BaseModel):
    id: str
    original_apk: str
    status: str
    processing_time: float
    timestamp: str
    analysis_result: Optional[Dict]
    injection_result: Optional[Dict]

# Simpan informasi proses
process_registry = {}

def get_system_uptime():
    """Dapatkan uptime sistem"""
    # Dalam implementasi nyata, ini akan melacak waktu mulai sistem
    return "00:15:30"  # Contoh

def get_system_stats():
    """Dapatkan statistik sistem"""
    # Dalam implementasi nyata, ini akan mendapatkan data aktual dari sistem
    return {
        "cpu_usage": 25.3,
        "memory_usage": 45.7,
        "active_users": 3
    }

def scan_process_reports() -> List[ProcessInfo]:
    """Scan direktori untuk laporan proses"""
    reports = []
    
    # Scan file analisis
    for analysis_file in RESULTS_DIR.glob("*_analysis.json"):
        try:
            with open(analysis_file, 'r') as f:
                data = json.load(f)
                
            process_id = analysis_file.stem.replace('_analysis', '')
            original_apk = data.get('apk_path', 'Unknown')
            
            # Check jika ada file injeksi terkait
            injection_file = RESULTS_DIR / f"{process_id}_injection.json"
            injection_result = None
            if injection_file.exists():
                with open(injection_file, 'r') as f:
                    injection_result = json.load(f)
            
            reports.append(ProcessInfo(
                id=process_id,
                original_apk=Path(original_apk).name if original_apk != 'Unknown' else analysis_file.stem.replace('_analysis', ''),
                status="Completed" if injection_result and injection_result.get('success', False) else "Processing",
                processing_time=injection_result.get('processing_time', 0) if injection_result else 0,
                timestamp=data.get('timestamp', ''),
                analysis_result=data.get('analysis_result'),
                injection_result=injection_result
            ))
        except Exception as e:
            print(f"Error reading {analysis_file}: {e}")
    
    # Urutkan berdasarkan timestamp terbaru
    reports.sort(key=lambda x: x.timestamp, reverse=True)
    return reports[:50]  # Batasi 50 terbaru

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Halaman utama dashboard"""
    # Buat template HTML dasar jika belum ada
    template_path = TEMPLATES_DIR / "dashboard.html"
    if not template_path.exists():
        # Buat template HTML dasar
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Crack Pro v3.0 - Dashboard</title>
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
        .process-table th {
            background-color: #f8f9fc;
        }
        .table-hover tbody tr:hover {
            background-color: rgba(78, 115, 223, 0.05);
        }
    </style>
</head>
<body id="page-top">
    <div id="wrapper">
        <div id="content-wrapper" class="d-flex flex-column">
            <div id="content">
                <div class="container-fluid">
                    <div class="d-sm-flex align-items-center justify-content-between mb-4">
                        <h1 class="h3 mb-0 text-gray-800"><i class="fas fa-shield-alt me-2"></i>Cyber Crack Pro v3.0 Dashboard</h1>
                        <a href="#" class="d-none d-sm-inline-block btn btn-sm btn-primary shadow-sm">
                            <i class="fas fa-download fa-sm text-white-50"></i> Generate Report
                        </a>
                    </div>

                    <!-- System Status Cards -->
                    <div class="row">
                        <div class="col-xl-3 col-md-6 mb-4">
                            <div class="card border-left-primary shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                                Bot Status</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">
                                                <span class="status-indicator status-active"></span>
                                                Active
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
                            <div class="card border-left-success shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                                Successful Processes</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800" id="successful-count">0</div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-check-circle fa-2x text-gray-300"></i>
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
                                                Active Users</div>
                                            <div class="row no-gutters align-items-center">
                                                <div class="col-auto">
                                                    <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800" id="active-users">0</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-users fa-2x text-gray-300"></i>
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

                    <!-- Process Info and Stats -->
                    <div class="row">
                        <div class="col-lg-8 mb-4">
                            <div class="card shadow mb-4">
                                <div class="card-header py-3">
                                    <h6 class="m-0 font-weight-bold text-primary">Recent Processing Activity</h6>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-bordered" id="processesTable" width="100%" cellspacing="0">
                                            <thead>
                                                <tr>
                                                    <th>ID</th>
                                                    <th>Original APK</th>
                                                    <th>Status</th>
                                                    <th>Time (s)</th>
                                                    <th>Timestamp</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody id="processes-body">
                                                <!-- Data will be populated by JavaScript -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="col-lg-4 mb-4">
                            <div class="card shadow mb-4">
                                <div class="card-header py-3">
                                    <h6 class="m-0 font-weight-bold text-primary">System Statistics</h6>
                                </div>
                                <div class="card-body">
                                    <div class="chart-pie pt-4">
                                        <div class="text-center">
                                            <canvas id="statusChart"></canvas>
                                        </div>
                                    </div>
                                    <div class="text-center small mt-4">
                                        <span class="me-2">
                                            <i class="fas fa-circle text-success"></i> Successful
                                        </span>
                                        <span class="me-2">
                                            <i class="fas fa-circle text-warning"></i> Processing
                                        </span>
                                        <span class="me-2">
                                            <i class="fas fa-circle text-danger"></i> Failed
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div class="card shadow mb-4">
                                <div class="card-header py-3">
                                    <h6 class="m-0 font-weight-bold text-primary">System Resources</h6>
                                </div>
                                <div class="card-body">
                                    <h4 class="small font-weight-bold">CPU Usage <span class="float-right" id="cpu-percent">0%</span></h4>
                                    <div class="progress mb-3">
                                        <div id="cpu-progress" class="progress-bar bg-info" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                                    </div>
                                    
                                    <h4 class="small font-weight-bold">Memory Usage <span class="float-right" id="memory-percent">0%</span></h4>
                                    <div class="progress mb-3">
                                        <div id="memory-progress" class="progress-bar bg-warning" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    
    <script>
        // Fungsi untuk memperbarui data dashboard
        async function updateDashboard() {
            try {
                // Ambil data status sistem
                const statusResponse = await fetch('/api/system/status');
                const statusData = await statusResponse.json();
                
                document.getElementById('successful-count').textContent = statusData.successful_processes;
                document.getElementById('active-users').textContent = statusData.active_users;
                document.getElementById('uptime').textContent = statusData.uptime;
                
                // Perbarui progress bar
                document.getElementById('cpu-percent').textContent = statusData.cpu_usage + '%';
                document.getElementById('cpu-progress').style.width = statusData.cpu_usage + '%';
                document.getElementById('cpu-progress').ariaValueNow = statusData.cpu_usage;
                
                document.getElementById('memory-percent').textContent = statusData.memory_usage + '%';
                document.getElementById('memory-progress').style.width = statusData.memory_usage + '%';
                document.getElementById('memory-progress').ariaValueNow = statusData.memory_usage;
                
                // Ambil data proses
                const processesResponse = await fetch('/api/processes');
                const processesData = await processesResponse.json();
                
                // Update tabel proses
                updateProcessesTable(processesData);
                
                // Update chart
                updateStatusChart(processesData);
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        function updateProcessesTable(processes) {
            const tbody = document.getElementById('processes-body');
            tbody.innerHTML = '';
            
            processes.forEach(process => {
                const statusClass = process.status === 'Completed' ? 
                    (process.injection_result && process.injection_result.success ? 'success' : 'danger') : 
                    'warning';
                
                const statusText = process.status === 'Completed' ? 
                    (process.injection_result && process.injection_result.success ? 'Success' : 'Failed') : 
                    'Processing';
                
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${process.id.substring(0, 8)}...</td>
                    <td>${process.original_apk}</td>
                    <td>
                        <span class="badge bg-${statusClass}">${statusText}</span>
                    </td>
                    <td>${process.processing_time.toFixed(2)}</td>
                    <td>${new Date(process.timestamp).toLocaleString()}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewDetails('${process.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }
        
        function updateStatusChart(processes) {
            const successful = processes.filter(p => p.status === 'Completed' && p.injection_result && p.injection_result.success).length;
            const processing = processes.filter(p => p.status === 'Processing').length;
            const failed = processes.filter(p => p.status === 'Completed' && p.injection_result && !p.injection_result.success).length;
            
            const ctx = document.getElementById('statusChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Successful', 'Processing', 'Failed'],
                    datasets: [{
                        data: [successful, processing, failed],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107', 
                            '#dc3545'
                        ],
                        hoverBackgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545'
                        ],
                        hoverBorderColor: "rgba(234, 236, 244, 1)",
                    }],
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: "rgb(255,255,255)",
                            bodyFontColor: "#858796",
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            caretPadding: 10,
                        }
                    },
                    cutout: '80%',
                },
            });
        }
        
        function viewDetails(processId) {
            window.location.href = `/process/${processId}`;
        }
        
        // Perbarui dashboard setiap 5 detik
        setInterval(updateDashboard, 5000);
        updateDashboard(); // Panggil pertama kali
    </script>
</body>
</html>'''
        with open(template_path, 'w') as f:
            f.write(html_content)

    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/process/{process_id}", response_class=HTMLResponse)
async def process_detail(request: Request, process_id: str):
    """Halaman detail proses"""
    # Cari file laporan untuk proses ini
    analysis_file = RESULTS_DIR / f"{process_id}_analysis.json"
    injection_file = RESULTS_DIR / f"{process_id}_injection.json"
    
    analysis_data = None
    injection_data = None
    
    if analysis_file.exists():
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
    
    if injection_file.exists():
        with open(injection_file, 'r') as f:
            injection_data = json.load(f)
    
    # Buat template detail jika tidak ada
    detail_template = TEMPLATES_DIR / "process_detail.html"
    if not detail_template.exists():
        detail_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Process Detail - Cyber Crack Pro v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <a href="/" class="btn btn-secondary mb-3"><i class="fas fa-arrow-left"></i> Back to Dashboard</a>
                <div class="card">
                    <div class="card-header">
                        <h4>Process Detail: {{ process_id }}</h4>
                    </div>
                    <div class="card-body">
                        <h5>Analysis Information</h5>
                        {% if analysis_data %}
                            <pre>{{ analysis_data | tojson(indent=2) }}</pre>
                        {% else %}
                            <p>No analysis data available.</p>
                        {% endif %}
                        
                        <h5 class="mt-4">Injection Information</h5>
                        {% if injection_data %}
                            <pre>{{ injection_data | tojson(indent=2) }}</pre>
                        {% else %}
                            <p>No injection data available.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        with open(detail_template, 'w') as f:
            f.write(detail_content)
    
    return templates.TemplateResponse("process_detail.html", {
        "request": request, 
        "process_id": process_id,
        "analysis_data": analysis_data,
        "injection_data": injection_data
    })

@app.get("/api/system/status")
async def get_system_status():
    """API endpoint untuk mendapatkan status sistem"""
    processes = scan_process_reports()
    
    successful = len([p for p in processes if p.status == "Completed" and p.injection_result and p.injection_result.get('success', False)])
    failed = len([p for p in processes if p.status == "Completed" and p.injection_result and not p.injection_result.get('success', False)])
    processing = len([p for p in processes if p.status == "Processing"])
    
    stats = get_system_stats()
    
    status = SystemStatus(
        bot_running=True,  # Dalam implementasi nyata, ini akan dicek dari proses bot
        total_processes=len(processes),
        successful_processes=successful,
        failed_processes=failed,
        uptime=get_system_uptime(),
        cpu_usage=stats['cpu_usage'],
        memory_usage=stats['memory_usage'],
        active_users=stats['active_users']
    )
    
    return status

@app.get("/api/processes")
async def get_processes():
    """API endpoint untuk mendapatkan daftar proses"""
    processes = scan_process_reports()
    return processes

@app.get("/api/logs")
async def get_logs():
    """API endpoint untuk mendapatkan log sistem"""
    log_file = LOGS_DIR / "bot.log"
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()[-100:]  # Ambil 100 baris terakhir
        return {"logs": [line.strip() for line in lines]}
    else:
        return {"logs": []}

@app.post("/api/trigger-analysis")
async def trigger_analysis(apk_path: str):
    """API endpoint untuk memicu analisis manual (simulasi)"""
    # Dalam implementasi nyata, ini akan memicu proses analisis
    return {"message": f"Analysis triggered for {apk_path}", "status": "success"}

if __name__ == "__main__":
    print("📊 Starting Cyber Crack Pro v3.0 Web Dashboard...")
    print("🔗 Dashboard will be available at: http://localhost:8000")
    print("API endpoints available:")
    print("  • GET /api/system/status - System status")
    print("  • GET /api/processes - Recent processes")
    print("  • GET /api/logs - System logs")
    print("  • POST /api/trigger-analysis - Trigger analysis")
    print()
    print("🚀 Web dashboard is now running!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)