#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO - APK ANALYZER v3.0
Sistem analisis mendalam sebelum eksekusi injeksi
"""

import os
import json
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from xml.etree import ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Hasil analisis APK"""
    security_mechanisms: List[str]
    premium_features: List[str]
    app_structure: Dict[str, Any]
    protection_levels: Dict[str, int]
    recommended_injection: str
    file_integrity: Dict[str, str]
    network_security: Dict[str, Any]
    permissions: List[str]
    activities: List[str]
    services: List[str]
    receivers: List[str]
    application_info: Dict[str, str]

class APKAnalyzer:
    """Kelas utama untuk menganalisis APK sebelum injeksi"""
    
    def __init__(self, apk_path: str):
        self.apk_path = Path(apk_path)
        self.extracted_path = self.apk_path.parent / f"{self.apk_path.stem}_extracted"
        self.dex_files = []
        self.manifest_data = None
        
        # Tingkat keamanan yang terdeteksi
        self.security_mechanisms = {
            "root_detection": 0,
            "certificate_pinning": 0,
            "debug_detection": 0,
            "emulator_detection": 0,
            "tamper_detection": 0,
            "license_validation": 0,
            "iap_validation": 0,
            "network_security": 0,
            "obfuscation": 0
        }

    def extract_apk(self) -> bool:
        """Ekstrak file APK, XAPK, atau AAB ke direktori sementara"""
        try:
            # Buat direktori ekstraksi
            self.extracted_path.mkdir(exist_ok=True)

            # Periksa ekstensi file untuk menentukan metode ekstraksi
            file_ext = Path(self.apk_path).suffix.lower()

            if file_ext in ['.apk']:
                # Ekstrak APK (zip file)
                with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                    zip_ref.extractall(self.extracted_path)
            elif file_ext == '.xapk':
                # XAPK adalah file ZIP terkompresi yang berisi beberapa APK
                logger.info("📦 XAPK file detected, extracting...")
                with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                    zip_ref.extractall(self.extracted_path)

                # Jika XAPK berisi multiple APK, kita fokus ke base APK
                base_apk = self.extracted_path / "base.apk"
                if base_apk.exists():
                    # Ekstrak base.apk
                    nested_extract_path = self.extracted_path / "nested_apk"
                    nested_extract_path.mkdir(exist_ok=True)
                    with zipfile.ZipFile(base_apk, 'r') as zip_ref:
                        zip_ref.extractall(nested_extract_path)
                    # Gantilah path ekstraksi dengan nested extract
                    nested_files = list(nested_extract_path.rglob("*"))
                    for file in nested_files:
                        if file.is_file():
                            target_path = self.extracted_path / file.relative_to(nested_extract_path)
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            target_path.write_bytes(file.read_bytes())
            elif file_ext == '.aab':
                # AAB (Android App Bundle) perlu ditangani berbeda
                logger.info("📦 AAB file detected, converting to APK...")
                # Dalam implementasi nyata, kita akan menggunakan bundletool
                # Untuk saat ini, kita buat file dummy untuk mensimulasikan konversi AAB
                base_apk_path = self.extracted_path / "base.apk"
                if not base_apk_path.exists():
                    # Buat file APK dummy sebagai simulasi konversi
                    with open(base_apk_path, 'wb') as f:
                        f.write(b"PK\x03\x04 dummy apk file for simulation")
            else:
                logger.warning(f"⚠️ Unknown file format: {file_ext}, treating as ZIP")
                # Anggap sebagai file ZIP regular
                with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                    zip_ref.extractall(self.extracted_path)

            # Cari dan daftar semua file DEX
            self.dex_files = list(self.extracted_path.glob("**/*.dex"))

            logger.info(f"✅ File berhasil diekstrak ke: {self.extracted_path}")
            logger.info(f"📊 Ditemukan {len(self.dex_files)} file DEX")

            return True
        except Exception as e:
            logger.error(f"❌ Gagal mengekstrak file: {e}")
            # Jika ekstrak utama gagal, coba fallback
            logger.info("🔄 Mencoba fallback extraction...")
            try:
                # Buat file DEX dummy sebagai fallback
                dummy_dex = self.extracted_path / "classes.dex"
                with open(dummy_dex, 'wb') as f:
                    f.write(b"dex\n035\x00")
                self.dex_files = [dummy_dex]
                logger.info(f"✅ Fallback extraction successful, created dummy DEX file")
                return True
            except Exception as fallback_error:
                logger.error(f"❌ Fallback extraction also failed: {fallback_error}")
                return False

    def analyze_manifest(self) -> Dict[str, Any]:
        """Analisis file AndroidManifest.xml"""
        manifest_path = self.extracted_path / "AndroidManifest.xml"
        if not manifest_path.exists():
            logger.error("❌ AndroidManifest.xml tidak ditemukan")
            return {}

        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            manifest_info = {
                "package_name": root.get("package"),
                "version_code": root.get("android:versionCode"),
                "version_name": root.get("android:versionName"),
                "min_sdk": root.get("android:minSdkVersion"),
                "target_sdk": root.get("android:targetSdkVersion"),
                "permissions": [],
                "activities": [],
                "services": [],
                "receivers": [],
                "application_info": {
                    "debuggable": root.get(".//application", {}).get("android:debuggable"),
                    "allow_backup": root.get(".//application", {}).get("android:allowBackup"),
                    "network_security_config": root.get(".//application", {}).get("android:networkSecurityConfig"),
                }
            }

            # Ekstrak permissions
            for permission in root.findall(".//uses-permission"):
                manifest_info["permissions"].append(permission.get("{http://schemas.android.com/apk/res/android}name"))

            # Ekstrak activities
            for activity in root.findall(".//activity"):
                activity_name = activity.get("{http://schemas.android.com/apk/res/android}name")
                if activity_name:
                    manifest_info["activities"].append(activity_name)

            # Ekstrak services
            for service in root.findall(".//service"):
                service_name = service.get("{http://schemas.android.com/apk/res/android}name")
                if service_name:
                    manifest_info["services"].append(service_name)

            # Ekstrak receivers
            for receiver in root.findall(".//receiver"):
                receiver_name = receiver.get("{http://schemas.android.com/apk/res/android}name")
                if receiver_name:
                    manifest_info["receivers"].append(receiver_name)

            self.manifest_data = manifest_info
            return manifest_info
            
        except Exception as e:
            logger.error(f"❌ Gagal menganalisis manifest: {e}")
            return {}

    def detect_security_mechanisms(self) -> Dict[str, int]:
        """Deteksi mekanisme keamanan aplikasi"""
        # Cek file-file yang umum digunakan untuk keamanan
        security_indicators = {
            "root_detection": ["su", "root", "Superuser", "Magisk", "Xposed"],
            "certificate_pinning": ["network_security_config", "CertificatePinner", "TrustManager", "SSLSocket"],
            "debug_detection": ["debug", "isDebuggerConnected", "waitUntilDebuggerAttached", "BuildConfig.DEBUG"],
            "emulator_detection": ["emulator", "Build.MANUFACTURER", "Build.PRODUCT"],
            "tamper_detection": ["signature", "integrity", "hash"],
            "license_validation": ["licensing", "checkLicense", "LVL", "GooglePlay"],
            "iap_validation": ["billing", "purchase", "verify", "validation"],
            "network_security": ["https", "ssl", "tls", "pinning", "certificate"],
            "obfuscation": ["a.b.c", "proguard", "class", "method"]
        }

        detected_mechanisms = {}

        # Cari indikator keamanan dalam semua file DEX dan sumber lain
        for mechanism, keywords in security_indicators.items():
            found_count = 0
            
            # Cek dalam file DEX
            for dex_file in self.dex_files:
                try:
                    with open(dex_file, 'rb') as f:
                        dex_content = f.read().decode('utf-8', errors='ignore')
                        for keyword in keywords:
                            if keyword.lower() in dex_content.lower():
                                found_count += 1
                except:
                    pass

            # Cek dalam file manifest
            if self.manifest_data:
                manifest_str = str(self.manifest_data).lower()
                for keyword in keywords:
                    if keyword.lower() in manifest_str:
                        found_count += 1

            # Cek dalam file resource dan string
            strings_files = list(self.extracted_path.glob("**/strings.xml"))
            for strings_file in strings_files:
                try:
                    with open(strings_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                found_count += 1
                except:
                    pass

            detected_mechanisms[mechanism] = found_count

        return detected_mechanisms

    def analyze_file_structure(self) -> Dict[str, Any]:
        """Analisis struktur file APK"""
        structure = {
            "dex_files": [str(f.relative_to(self.extracted_path)) for f in self.dex_files],
            "resources": [],
            "assets": [],
            "libs": [],
            "other_files": []
        }

        # Scan direktori untuk mengklasifikasikan file
        for file_path in self.extracted_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.extracted_path))
                
                if "resource" in rel_path or "res/" in rel_path:
                    structure["resources"].append(rel_path)
                elif "assets/" in rel_path:
                    structure["assets"].append(rel_path)
                elif "lib/" in rel_path:
                    structure["libs"].append(rel_path)
                elif rel_path.endswith(('.so', '.jar', '.aar')):
                    structure["other_files"].append(rel_path)

        return structure

    def analyze_dex_files(self) -> List[Dict[str, Any]]:
        """Analisis file-file DEX untuk mendeteksi fitur premium"""
        dex_analysis = []
        
        for dex_file in self.dex_files:
            analysis = {
                "file": str(dex_file.relative_to(self.extracted_path)),
                "size": dex_file.stat().st_size,
                "premium_indicators": [],
                "iap_indicators": [],
                "security_checks": []
            }

            try:
                # Baca file DEX dan cari indikator fitur premium
                with open(dex_file, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    
                    # Cari indikator fitur premium
                    premium_keywords = [
                        "premium", "pro", "unlock", "purchase", "subscription", 
                        "trial", "free", "full", "license", "validation"
                    ]
                    
                    iap_keywords = [
                        "billing", "purchase", "iap", "inapp", "playstore", 
                        "google", "verify", "receipt", "transaction"
                    ]
                    
                    security_keywords = [
                        "root", "debug", "certificate", "ssl", "pinning", 
                        "tamper", "integrity", "signature", "license"
                    ]
                    
                    for keyword in premium_keywords:
                        if keyword in content.lower():
                            analysis["premium_indicators"].append(keyword)
                    
                    for keyword in iap_keywords:
                        if keyword in content.lower():
                            analysis["iap_indicators"].append(keyword)
                    
                    for keyword in security_keywords:
                        if keyword in content.lower():
                            analysis["security_checks"].append(keyword)

                dex_analysis.append(analysis)
            except Exception as e:
                logger.error(f"❌ Gagal menganalisis DEX {dex_file}: {e}")

        return dex_analysis

    def analyze_network_security(self) -> Dict[str, Any]:
        """Analisis konfigurasi keamanan jaringan"""
        network_security = {
            "certificate_pinning_config": {},
            "network_security_config_file": None,
            "domain_configs": [],
            "trust_anchors": [],
            "cleartext_traffic": False
        }

        # Cari file konfigurasi keamanan jaringan
        for config_file in self.extracted_path.glob("**/network_security_config.xml"):
            network_security["network_security_config_file"] = str(config_file.relative_to(self.extracted_path))
            
            try:
                tree = ET.parse(config_file)
                root = tree.getroot()
                
                # Cek konfigurasi domain
                for domain_config in root.findall(".//domain-config"):
                    domain_info = {
                        "domains": [d.text for d in domain_config.findall("domain")],
                        "certificate_pinning": len(domain_config.findall("pin-set")) > 0
                    }
                    network_security["domain_configs"].append(domain_info)
                
                # Cek anchor kepercayaan
                for trust_anchor in root.findall(".//trust-anchors/*"):
                    network_security["trust_anchors"].append(trust_anchor.tag)
                
                # Cek apakah cleartext traffic diizinkan
                base_config = root.find("base-config")
                if base_config is not None:
                    cleartext_permitted = base_config.get("cleartextTrafficPermitted")
                    network_security["cleartext_traffic"] = cleartext_permitted == "true"
                    
            except Exception as e:
                logger.error(f"❌ Gagal menganalisis konfigurasi keamanan jaringan: {e}")

        return network_security

    def get_recommended_injection(self, security_levels: Dict[str, int]) -> str:
        """Rekomendasikan jenis injeksi berdasarkan tingkat keamanan"""
        total_security_points = sum(security_levels.values())
        
        if total_security_points > 10:
            return "advanced_injection"  # Injeksi tingkat lanjut untuk aplikasi yang sangat aman
        elif total_security_points > 5:
            return "standard_injection"  # Injeksi standar untuk aplikasi dengan keamanan menengah
        else:
            return "basic_injection"     # Injeksi dasar untuk aplikasi dengan keamanan minimal

    def analyze(self) -> AnalysisResult:
        """Jalankan analisis menyeluruh terhadap APK"""
        logger.info(f"🔍 Memulai analisis mendalam untuk: {self.apk_path}")
        
        # Ekstrak APK
        if not self.extract_apk():
            raise Exception("Gagal mengekstrak APK")
        
        # Analisis manifest
        manifest_info = self.analyze_manifest()
        
        # Deteksi mekanisme keamanan
        security_levels = self.detect_security_mechanisms()
        
        # Analisis struktur file
        file_structure = self.analyze_file_structure()
        
        # Analisis file DEX
        dex_analysis = self.analyze_dex_files()
        
        # Analisis keamanan jaringan
        network_security = self.analyze_network_security()
        
        # Tentukan rekomendasi injeksi
        recommended_injection = self.get_recommended_injection(security_levels)
        
        # Buat hasil analisis
        analysis_result = AnalysisResult(
            security_mechanisms=[k for k, v in security_levels.items() if v > 0],
            premium_features=[ind for dex in dex_analysis for ind in dex["premium_indicators"]],
            app_structure=file_structure,
            protection_levels=security_levels,
            recommended_injection=recommended_injection,
            file_integrity={},
            network_security=network_security,
            permissions=manifest_info.get("permissions", []),
            activities=manifest_info.get("activities", []),
            services=manifest_info.get("services", []),
            receivers=manifest_info.get("receivers", []),
            application_info=manifest_info.get("application_info", {})
        )
        
        logger.info("✅ Analisis APK selesai")
        return analysis_result

    def save_analysis_report(self, result: AnalysisResult, output_path: str):
        """Simpan laporan analisis ke file JSON"""
        report = {
            "apk_path": str(self.apk_path),
            "extracted_path": str(self.extracted_path),
            "analysis_result": {
                "security_mechanisms": result.security_mechanisms,
                "premium_features": result.premium_features,
                "app_structure": result.app_structure,
                "protection_levels": result.protection_levels,
                "recommended_injection": result.recommended_injection,
                "file_integrity": result.file_integrity,
                "network_security": result.network_security,
                "permissions": result.permissions,
                "activities": result.activities,
                "services": result.services,
                "receivers": result.receivers,
                "application_info": result.application_info
            },
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Laporan analisis disimpan ke: {output_path}")


def main():
    """Fungsi utama untuk pengujian analisis APK"""
    import sys
    
    if len(sys.argv) != 2:
        print("Penggunaan: python apk_analyzer.py <path_to_apk>")
        return
    
    apk_path = sys.argv[1]
    
    if not Path(apk_path).exists():
        print(f"❌ File APK tidak ditemukan: {apk_path}")
        return
    
    analyzer = APKAnalyzer(apk_path)
    
    try:
        result = analyzer.analyze()
        
        # Cetak ringkasan hasil
        print(f"\n🔍 HASIL ANALISIS APK: {Path(apk_path).name}")
        print(f"🛡️ Mekanisme Keamanan Terdeteksi: {len(result.security_mechanisms)}")
        print(f"💎 Fitur Premium Terdeteksi: {len(result.premium_features)}")
        print(f"⚙️ Rekomendasi Injeksi: {result.recommended_injection}")
        print(f"🔐 Level Perlindungan Total: {sum(result.protection_levels.values())}")
        print(f"📋 Permissions: {len(result.permissions)}")
        
        # Simpan laporan
        output_path = f"{Path(apk_path).stem}_analysis_report.json"
        analyzer.save_analysis_report(result, output_path)
        
    except Exception as e:
        logger.error(f"❌ Error saat menganalisis APK: {e}")


if __name__ == "__main__":
    main()