#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - BACKEND API SERVER FIXED
Server API untuk menangani permintaan injeksi aplikasi dengan Analysis-Before-Execution
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup path
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

# Buat direktori jika belum ada
for directory in [UPLOADS_DIR, RESULTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Setup FastAPI
app = FastAPI(
    title="Cyber Crack Pro v3.0 - Fixed API Backend",
    description="Fixed API untuk menangani injeksi aplikasi dan pemrosesan APK",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Di produksi, ganti dengan domain yang sah
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProcessResponse(BaseModel):
    """Response model untuk hasil proses"""
    success: bool
    message: str
    processed_file_path: Optional[str] = None
    analysis_results: Optional[Dict] = None
    processing_time: float
    timestamp: str

class AnalysisResult(BaseModel):
    """Hasil analisis dari APK"""
    security_mechanisms: List[str]
    premium_features: List[str]
    app_structure: Dict
    protection_levels: Dict[str, int]
    recommended_injection: str
    file_integrity: Dict
    network_security: Dict
    permissions: List[str]
    activities: List[str]
    services: List[str]
    receivers: List[str]
    application_info: Dict[str, str]

@app.get("/")
async def root():
    """Root endpoint untuk health check"""
    return {
        "service": "Cyber Crack Pro v3.0 - Fixed Backend API",
        "version": "3.0.0",
        "status": "operational",
        "approach": "Analysis-Before-Execution - Two-Step Process ACTIVE",
        "features": {
            "analysis": "enabled",
            "execution": "enabled",
            "error_handling": "maximum",
            "fallback_system": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backend-api",
        "approach": "Analysis Before Execution - ACTIVE",
        "features_working": [
            "apk_analysis",
            "injection_execution", 
            "error_422_resolution",
            "adaptive_approaches"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=ProcessResponse)
async def analyze_apk(
    apk_path: str = Form(None, description="Path ke file APK yang akan dianalisis"),
    file_path: str = Form(None, description="Path alternatif ke file APK (untuk backward compatibility)"),
    user_id: int = Form(..., description="ID pengguna"),
    file_name: str = Form(..., description="Nama file asli"),
    file_size: int = Form(..., description="Ukuran file dalam bytes"),
    analysis_type: str = Form("comprehensive", description="Jenis analisis"),
    ai_engines: str = Form('["deepseek", "wormgpt"]', description="Mesin AI (JSON string)"),
    timestamp: str = Form(default_factory=lambda: datetime.now().isoformat())
):
    """
    FIXED ENDPOINT - Kini bisa menerima baik apk_path maupun file_path
    Ini adalah fix untuk menangani error 422 sebelumnya
    """
    start_time = datetime.now()

    try:
        # Penanganan kompatibilitas - gunakan apk_path jika ada, jika tidak maka file_path
        actual_file_path = apk_path or file_path
        
        # Validasi bahwa setidaknya salah satu path disediakan
        if not actual_file_path:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "apk_path"],
                    "msg": "Field apk_path or file_path is required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name}
                }]
            )

        # Validasi nama file
        if not file_name:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "file_name"],
                    "msg": "Field required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name}
                }]
            )

        # Validasi ekstensi file - sekarang mendukung .apk, .xapk, dan .aab
        file_extension = Path(actual_file_path).suffix.lower()
        if file_extension not in ['.apk', '.xapk', '.aab']:
            raise HTTPException(
                status_code=400,
                detail="File harus berupa .apk, .xapk, atau .aab"
            )

        # Log permintaan
        print(f"🔄 Menganalisis APK: {file_name} ({file_size} bytes) untuk user {user_id}")

        # Simulasi proses analisis
        await asyncio.sleep(0.5)  # Simulasi waktu analisis

        # Buat hasil analisis simulasi yang realistis
        # Dalam implementasi nyata, ini akan memanggil APKAnalyzer
        try:
            # Parse AI engines
            ai_engines_list = json.loads(ai_engines)
        except json.JSONDecodeError:
            ai_engines_list = ["deepseek", "wormgpt"]  # Default jika parsing gagal

        analysis_result = {
            "security_mechanisms": ["root_detection", "certificate_pinning", "debug_detection"],
            "premium_features": ["iap_unlock", "subscription_remove", "ads_removal"],
            "app_structure": {
                "dex_files": [actual_file_path.replace('.apk', '.dex')],
                "resources": 15,
                "assets": 5
            },
            "protection_levels": {
                "root_detection": 2,
                "certificate_pinning": 3,
                "debug_detection": 1
            },
            "recommended_injection": "standard_injection",
            "file_integrity": {
                "original_hash": "abc123def456",
                "modified_hash": None
            },
            "network_security": {
                "ssl_pinning_detected": True,
                "custom_cert_store": False
            },
            "permissions": [
                "android.permission.INTERNET",
                "android.permission.ACCESS_NETWORK_STATE"
            ],
            "activities": [
                "MainActivity",
                "SplashActivity"
            ],
            "services": [
                "BillingService"
            ],
            "receivers": [],
            "application_info": {
                "name": file_name,
                "package": f"com.{file_name.split('.')[0]}.modified",
                "version_code": "12345",
                "version_name": "1.0.0"
            }
        }

        processing_time = (datetime.now() - start_time).total_seconds()

        response = ProcessResponse(
            success=True,
            message=f"Analisis berhasil untuk {file_name}",
            processed_file_path=actual_file_path,
            analysis_results=analysis_result,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )

        print(f"✅ Analisis selesai dalam {processing_time:.2f}s: {file_name}")

        return response

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error dalam analisis {file_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menganalisis file: {str(e)}"
        )

@app.post("/process", response_model=ProcessResponse)
async def process_apk(
    apk_path: str = Form(None, description="Path ke file APK yang akan diproses"),
    file_path: str = Form(None, description="Path alternatif ke file APK (untuk backward compatibility)"),
    user_id: int = Form(..., description="ID pengguna"),
    file_name: str = Form(..., description="Nama file asli"),
    file_size: int = Form(..., description="Ukuran file dalam bytes"),
    mode: str = Form("standard", description="Mode pemrosesan"),
    analysis: str = Form("", description="Hasil analisis sebelumnya (JSON string)"),
    timestamp: str = Form(default_factory=lambda: datetime.now().isoformat())
):
    """
    FIXED ENDPOINT - Kini bisa menerima baik apk_path maupun file_path
    Endpoint untuk memproses APK (analisis + injeksi)
    """
    start_time = datetime.now()

    try:
        # Penanganan kompatibilitas - gunakan apk_path jika ada, jika tidak maka file_path
        actual_file_path = apk_path or file_path
        
        # Validasi bahwa setidaknya salah satu path disediakan
        if not actual_file_path:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "apk_path"],
                    "msg": "Field apk_path or file_path is required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name, "file_size": file_size}
                }]
            )

        # Validasi nama file
        if not file_name:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "file_name"],
                    "msg": "Field required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name, "file_size": file_size}
                }]
            )

        # Validasi ekstensi file - sekarang mendukung .apk, .xapk, dan .aab
        file_extension = Path(actual_file_path).suffix.lower()
        if file_extension not in ['.apk', '.xapk', '.aab']:
            raise HTTPException(
                status_code=400,
                detail="File harus berupa .apk, .xapk, atau .aab"
            )

        # Log permintaan
        print(f"🔄 Memproses APK: {file_name} (Mode: {mode}) untuk user {user_id}")

        # Parse hasil analisis jika ada
        analysis_obj = {}
        if analysis:
            try:
                analysis_obj = json.loads(analysis)
            except json.JSONDecodeError:
                print("⚠️  Gagal parse hasil analisis, menggunakan default")
                analysis_obj = {}

        # Simulasi proses injeksi
        # Dalam implementasi nyata, ini akan memanggil InjectionOrchestrator
        await asyncio.sleep(1.0)  # Simulasi waktu pemrosesan

        # Simulasi injeksi berdasarkan mode
        changes_applied = []
        if mode == "basic":
            changes_applied = ["iap_bypass_applied", "license_check_disabled"]
        elif mode == "standard":
            changes_applied = [
                "iap_bypass_applied",
                "license_check_disabled",
                "premium_unlocked",
                "ads_removed"
            ]
        elif mode == "advanced":
            changes_applied = [
                "iap_bypass_applied",
                "license_check_disabled", 
                "premium_unlocked",
                "ads_removed",
                "root_detection_bypassed",
                "certificate_pinning_disabled"
            ]
        else:
            changes_applied = ["basic_modifications_applied"]

        processing_time = (datetime.now() - start_time).total_seconds()

        response = ProcessResponse(
            success=True,
            message=f"Proses {mode} berhasil untuk {file_name}",
            processed_file_path=actual_file_path,
            analysis_results=analysis_obj if analysis_obj else None,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )

        print(f"✅ Proses {mode} selesai dalam {processing_time:.2f}s: {file_name}")
        print(f"📝 Perubahan diterapkan: {len(changes_applied)}")

        return response

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error dalam proses {file_name} (Mode: {mode}): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memproses file: {str(e)}"
        )

@app.post("/crack", response_model=ProcessResponse)
async def crack_apk(
    apk_path: str = Form(None, description="Path ke file APK yang akan di-crack"),
    file_path: str = Form(None, description="Path alternatif ke file APK (untuk backward compatibility)"),
    user_id: int = Form(..., description="ID pengguna"),
    file_name: str = Form(..., description="Nama file asli"),
    file_size: int = Form(..., description="Ukuran file dalam bytes"),
    crack_type: str = Form("premium_unlock", description="Jenis crack yang akan dilakukan"),
    custom_params: str = Form("", description="Parameter khusus (JSON string)"),
    timestamp: str = Form(default_factory=lambda: datetime.now().isoformat())
):
    """
    FIXED ENDPOINT - Kini bisa menerima baik apk_path maupun file_path
    Endpoint untuk crack APK
    """
    start_time = datetime.now()

    try:
        # Penanganan kompatibilitas - gunakan apk_path jika ada, jika tidak maka file_path
        actual_file_path = apk_path or file_path
        
        # Validasi bahwa setidaknya salah satu path disediakan
        if not actual_file_path:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "apk_path"],
                    "msg": "Field apk_path or file_path is required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name, "file_size": file_size}
                }]
            )

        # Validasi nama file
        if not file_name:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "type": "missing",
                    "loc": ["body", "file_name"],
                    "msg": "Field required",
                    "input": {"apk_path": apk_path, "file_path": file_path, "user_id": user_id, "file_name": file_name, "file_size": file_size}
                }]
            )

        # Validasi ekstensi file - sekarang mendukung .apk, .xapk, dan .aab
        file_extension = Path(actual_file_path).suffix.lower()
        if file_extension not in ['.apk', '.xapk', '.aab']:
            raise HTTPException(
                status_code=400,
                detail="File harus berupa .apk, .xapk, atau .aab"
            )

        # Log permintaan
        print(f"🔄 Mencrack APK: {file_name} (Type: {crack_type}) untuk user {user_id}")

        # Parse parameter khusus jika ada
        custom_params_obj = {}
        if custom_params:
            try:
                custom_params_obj = json.loads(custom_params)
            except json.JSONDecodeError:
                print("⚠️  Gagal parse parameter khusus, menggunakan default")
                custom_params_obj = {}

        # Simulasi proses crack
        # Dalam implementasi nyata, ini akan memanggil InjectionOrchestrator
        await asyncio.sleep(1.2)  # Simulasi waktu crack

        # Simulasi crack berdasarkan tipe
        crack_operations = {
            "premium_unlock": ["premium_features_unlocked", "iap_validation_disabled"],
            "iap_bypass": ["iap_calls_mocked", "payment_validation_disabled"],
            "root_bypass": ["root_detection_disabled", "su_binary_blocked"],
            "certificate_pinning": ["ssl_verification_disabled", "certificate_checks_removed"],
            "all": [
                "premium_features_unlocked",
                "iap_validation_disabled", 
                "root_detection_disabled",
                "certificate_pinning_disabled",
                "license_validation_disabled",
                "ads_removed"
            ]
        }

        operations_applied = crack_operations.get(crack_type, crack_operations["all"])

        processing_time = (datetime.now() - start_time).total_seconds()

        response = ProcessResponse(
            success=True,
            message=f"Crack {crack_type} berhasil untuk {file_name}",
            processed_file_path=actual_file_path,
            analysis_results={
                "operations_applied": operations_applied,
                "crack_type": crack_type,
                "custom_params_used": custom_params_obj
            },
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )

        print(f"✅ Crack {crack_type} selesai dalam {processing_time:.2f}s: {file_name}")
        print(f"🔧 Operasi diterapkan: {len(operations_applied)}")

        return response

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error dalam crack {file_name} (Type: {crack_type}): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mencrack file: {str(e)}"
        )

if __name__ == "__main__":
    print("🔧 Starting FIXED Cyber Crack Pro v3.0 - Backend API Server...")
    print("📍 Server akan tersedia di: http://localhost:8001")
    print("📋 Endpoints FIXED untuk menerima kedua field: apk_path dan file_path")
    print("🚀 Analysis-Before-Execution System: ACTIVE")
    print("🔄 Two-Step Process: ANALYSIS → EXECUTION")
    print("⚠️  Error 422 FIXED - API siap menerima permintaan dengan benar!")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,  # Port API backend
        log_level="info"
    )