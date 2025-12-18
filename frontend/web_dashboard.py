#!/usr/bin/env python3
"""
🤖 CYBER CRACK PRO Web Dashboard
Advanced web interface for APK analysis and modification
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from starlette.requests import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cyber Crack Pro Dashboard",
    description="Advanced Web Interface for APK Analysis and Modification",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose custom headers for download URLs
    expose_headers=["Content-Disposition"]
)

# Static files and templates
STATIC_DIR = Path("frontend/static")
STATIC_DIR.mkdir(exist_ok=True)

TEMPLATE_DIR = Path("frontend/templates")
TEMPLATE_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Global configuration
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create basic HTML template
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Crack Pro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@1.8.4"></script>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .card {
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
        }
        .form-control, .form-select {
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-transparent">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">🛡️ Cyber Crack Pro</a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card p-5 text-center text-white">
                    <h1 class="display-4 mb-4">🚀 Cyber Crack Pro Dashboard</h1>
                    <p class="lead">AI-Powered APK Analysis & Modification Platform</p>
                    
                    <div class="row g-4 mt-5">
                        <div class="col-md-4">
                            <div class="bg-white bg-opacity-20 p-3 rounded">
                                <i class="fas fa-bolt fa-3x mb-3"></i>
                                <h3>Fast</h3>
                                <p>3-6s per APK</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="bg-white bg-opacity-20 p-3 rounded">
                                <i class="fas fa-brain fa-3x mb-3"></i>
                                <h3>AI-Powered</h3>
                                <p>Smart Analysis</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="bg-white bg-opacity-20 p-3 rounded">
                                <i class="fas fa-shield-alt fa-3x mb-3"></i>
                                <h3>100+ Features</h3>
                                <p>Complete Toolkit</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-lg-8 mx-auto">
                <div class="card p-4 bg-white bg-opacity-90">
                    <h3 class="text-center mb-4"><i class="fas fa-file-upload"></i> Upload APK for Analysis</h3>
                    
                    <form id="uploadForm" hx-post="/api/upload" hx-target="#result" hx-swap="innerHTML" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="apkFile" class="form-label">APK File</label>
                            <input type="file" class="form-control" id="apkFile" name="file" accept=".apk" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="category" class="form-label">Category</label>
                            <select class="form-select" id="category" name="category">
                                <option value="">Auto-Detect (Recommended)</option>
                                <option value="login_bypass">Login Bypass</option>
                                <option value="iap_crack">In-App Purchase Crack</option>
                                <option value="game_mods">Game Modifications</option>
                                <option value="premium_unlock">Premium Unlock</option>
                                <option value="root_bypass">Root Detection Bypass</option>
                                <option value="ssl_bypass">SSL Certificate Bypass</option>
                                <option value="debug_bypass">Anti-Debug Bypass</option>
                                <option value="license_crack">License Crack</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-bolt"></i> Start Analysis
                        </button>
                    </form>
                    
                    <div id="result" class="mt-4"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
    <script>
        document.getElementById('uploadForm').addEventListener('submit', function() {
            document.querySelector('.btn-primary').disabled = true;
            document.querySelector('.btn-primary').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        });
    </script>
</body>
</html>
"""

# Write index template
(Path(TEMPLATE_DIR) / "index.html").write_text(index_html)

class WebSocketManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

websocket_manager = WebSocketManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process WebSocket messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.post("/api/upload")
async def upload_apk(
    file: UploadFile = File(...),
    category: Optional[str] = "",
    features: Optional[str] = ""
):
    """Upload APK for processing"""
    try:
        # Validate file
        if not file.filename.endswith('.apk'):
            raise HTTPException(status_code=400, detail="File must be .apk")
        
        # Create upload directory
        user_upload_dir = UPLOAD_DIR / f"user_{hash(file.filename)}"
        user_upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = user_upload_dir / f"{file.filename}"
        content = await file.read()
        file_path.write_bytes(content)
        
        # Send to orchestrator
        async with aiohttp.ClientSession() as session:
            payload = {
                "apk_path": str(file_path),
                "category": category,
                "user_id": "web_user",
                "origin": "web_dashboard"
            }
            
            if features:
                payload["features"] = features.split(",")
            
            async with session.post(f"{ORCHESTRATOR_URL}/analyze", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Create response with download link
                    return JSONResponse(content={
                        "status": "success",
                        "job_id": result.get("job_id", "unknown"),
                        "message": f"File {file.filename} uploaded and analysis started",
                        "estimated_time": "5-15 seconds",
                        "progress_url": f"/api/progress/{result.get('job_id', 'unknown')}"
                    })
                else:
                    error_detail = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_detail)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress/{job_id}")
async def get_progress(job_id: str):
    """Get job progress"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ORCHESTRATOR_URL}/api/job/{job_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException(status_code=response.status, detail="Job not found")
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/download/{job_id}")
async def download_result(job_id: str):
    """Download processed result"""
    try:
        # Get job result to find the modified APK path
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ORCHESTRATOR_URL}/api/job/{job_id}") as response:
                if response.status == 200:
                    job_data = await response.json()
                    
                    result_path = job_data.get("result", {}).get("modified_apk_path")
                    if not result_path:
                        raise HTTPException(status_code=404, detail="Result not ready")
                    
                    if not os.path.exists(result_path):
                        raise HTTPException(status_code=404, detail="Result file not found")
                    
                    return FileResponse(
                        path=result_path,
                        filename=f"MODIFIED_{os.path.basename(result_path)}",
                        media_type="application/vnd.android.package-archive"
                    )
                else:
                    raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ORCHESTRATOR_URL}/api/stats") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "total_processed": 0,
                        "success_rate": "0%",
                        "active_workers": 0,
                        "queue_size": 0
                    }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/recent-jobs")
async def get_recent_jobs(limit: int = 20):
    """Get recent jobs"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ORCHESTRATOR_URL}/api/recent?limit={limit}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "web-dashboard",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/features")
async def get_features():
    """Get all available features"""
    features = [
        {"name": "login_bypass", "category": "authentication", "description": "Bypass login systems"},
        {"name": "iap_crack", "category": "billing", "description": "Crack in-app purchases"},
        {"name": "certificate_pinning_bypass", "category": "security", "description": "Bypass SSL pinning"},
        {"name": "root_detection_bypass", "category": "security", "description": "Bypass root detection"},
        {"name": "anti_debug_bypass", "category": "security", "description": "Bypass anti-debug"},
        {"name": "license_crack", "category": "licensing", "description": "Crack license verification"},
        {"name": "game_modifications", "category": "games", "description": "Modify game behavior"},
        {"name": "premium_unlock", "category": "features", "description": "Unlock premium features"},
        {"name": "ads_removal", "category": "advertising", "description": "Remove advertisements"},
        {"name": "data_extraction", "category": "data", "description": "Extract application data"}
    ]
    return {"features": features, "count": len(features)}

# Error handlers
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "path": str(request.url)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "web_dashboard:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )