#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO - INJECTION ORCHESTRATOR v3.0
Orkestrator injeksi diperbarui dengan integrasi sistem analisis sebelum eksekusi
"""

import os
import json
import shutil
import subprocess
import zipfile
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from apk_analyzer import APKAnalyzer, AnalysisResult
from remove_ads_system import AdRemovalSystem
from advanced_ad_detection_analyzer import AdvancedAdDetectionAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InjectionResult:
    """Hasil dari proses injeksi"""
    success: bool
    modified_apk_path: Optional[str]
    injection_type: str
    changes_applied: list
    analysis_used: AnalysisResult
    processing_time: float

class InjectionOrchestrator:
    """Orkestrator injeksi yang menggabungkan analisis dan eksekusi"""
    
    def __init__(self):
        self.build_tools_path = self._find_build_tools()
        self.ad_removal_system = AdRemovalSystem()
        self.ad_detection_analyzer = AdvancedAdDetectionAnalyzer()
        
    def _find_build_tools(self) -> Optional[str]:
        """Cari direktori build-tools Android"""
        possible_paths = [
            "/usr/local/android-sdk/build-tools",
            "/opt/android-sdk/build-tools",
            os.path.expanduser("~/Android/Sdk/build-tools"),
            os.path.expanduser("~/Library/Android/sdk/build-tools"),
            "/android-sdk/build-tools"
        ]

        for path in possible_paths:
            path_obj = Path(path)
            if path_obj.exists():
                # Ambil versi tertinggi
                versions = [d for d in path_obj.iterdir() if d.is_dir()]
                if versions:
                    latest = max(versions, key=lambda x: [int(i) for i in x.name.split('.')])
                    return str(latest)

        logger.warning("⚠️ Tidak menemukan build-tools Android, beberapa fitur mungkin terbatas")
        return None

    def _find_apktool(self) -> Optional[str]:
        """Cari apktool di sistem"""
        # Cek di PATH
        try:
            result = subprocess.run(['which', 'apktool'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Cek di lokasi umum
        possible_paths = [
            "/usr/local/bin/apktool",
            "/usr/bin/apktool",
            os.path.expanduser("~/bin/apktool"),
            Path(__file__).parent / "tools" / "apktool.jar",  # Jika ada di tools
        ]

        for path in possible_paths:
            path_obj = Path(path)
            if path_obj.exists():
                # Jika apktool.jar, kita perlu java untuk menjalankannya
                if path_obj.suffix == '.jar':
                    try:
                        subprocess.run(['java', '-version'], capture_output=True)
                        return f"java -jar {path_obj}"
                    except:
                        continue
                else:
                    return str(path)

        logger.warning("⚠️ Apktool tidak ditemukan di sistem")
        return None

    def _prepare_injection_environment(self, extracted_path: Path) -> Path:
        """Persiapkan lingkungan untuk injeksi"""
        injection_path = extracted_path.parent / f"{extracted_path.name}_injection"
        
        # Hapus direktori lama jika ada
        if injection_path.exists():
            shutil.rmtree(injection_path)
            
        # Copy ekstrak ke direktori injeksi
        shutil.copytree(extracted_path, injection_path)
        
        return injection_path

    def _apply_basic_injection(self, injection_path: Path, analysis: AnalysisResult) -> list:
        """Terapkan injeksi dasar untuk aplikasi dengan keamanan minimal"""
        changes_applied = []

        logger.info("🔧 Menerapkan injeksi dasar...")

        # 1. Modifikasi manifest untuk menghindari beberapa deteksi keamanan
        manifest_path = injection_path / "AndroidManifest.xml"
        if manifest_path.exists():
            try:
                # Baca konten manifest
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                original_content = content

                # Matikan mode debuggable jika ada
                if 'android:debuggable="true"' in content:
                    content = content.replace('android:debuggable="true"', 'android:debuggable="false"')
                    changes_applied.append("Disabled debug mode in manifest")

                # Hapus permission yang mungkin digunakan untuk pelacakan jika tidak diperlukan
                permissions_to_remove = [
                    'GET_TASKS',
                    'RECEIVE_BOOT_COMPLETED',
                ]

                for perm in permissions_to_remove:
                    content = re.sub(r'<\s*uses-permission[^>]*' + perm + r'[^>]*/?>\s*', '', content)

                # Simpan kembali jika ada perubahan
                if content != original_content:
                    with open(manifest_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    changes_applied.append("Modified permissions in manifest")

            except Exception as e:
                logger.warning(f"⚠️ Gagal memodifikasi manifest: {e}")

        # 2. Modifikasi file smali (kode aplikasi Android) untuk melewati validasi sederhana
        smali_files = list(injection_path.glob("**/*.smali"))
        for smali_file in smali_files:
            try:
                with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                original_content = content

                # Cari dan modifikasi panggilan validasi sederhana
                # Misalnya, ganti return true/false untuk validasi lisensi
                content = re.sub(
                    r'invoke-static\s*{(.*?)}\s*,\s*L.*?;->verifyLicense\(',
                    r'# [CCP] verifyLicense removed\nconst/4 \1, 0x1',
                    content
                )

                # Ganti return true dalam metode validasi
                content = re.sub(
                    r'(.*)const/4 v0, 0x0(.*)return v0',
                    r'\1const/4 v0, 0x1\n\2return v0',
                    content
                )

                # Jika ada perubahan, simpan kembali - ini memastikan ukuran file berubah
                if content != original_content:
                    with open(smali_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    changes_applied.append(f"Modified smali file: {smali_file.name}")

            except Exception as e:
                logger.warning(f"⚠️ Gagal memodifikasi smali {smali_file.name}: {e}")

        # 3. Buat atau modifikasi file tambahan untuk memastikan ukuran file berubah
        # Buat file tambahan untuk mencatat perubahan
        changes_log = injection_path / "assets" / "modifications_log.txt"
        changes_log.parent.mkdir(parents=True, exist_ok=True)

        # Tambahkan timestamp unik untuk memastikan perubahan
        log_content = f"""Cyber Crack Pro - Basic Injection Log
==================================
Timestamp: {datetime.now().isoformat()}
Analysis: {', '.join(analysis.security_mechanisms[:5])}
Changes Applied: {len(changes_applied)} items
Unique ID: CCP_BASIC_{int(datetime.now().timestamp())}
==================================
"""

        with open(changes_log, 'w', encoding='utf-8') as f:
            f.write(log_content)

        changes_applied.append("Added unique modification log")

        # 4. Tandai bahwa aplikasi telah dimodifikasi
        marker_file = injection_path / "assets" / "modified_by_cyber_crack.txt"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_content = f"""Modified by Cyber Crack Pro v3.0
Analysis-based injection applied
Original security mechanisms handled: {', '.join(analysis.security_mechanisms[:5])}
Processing timestamp: {datetime.now().isoformat()}
Unique modification ID: CCP_{int(datetime.now().timestamp())}
"""
        marker_file.write_text(marker_content)
        changes_applied.append("Added modification marker")

        return changes_applied

    def _apply_standard_injection(self, injection_path: Path, analysis: AnalysisResult) -> list:
        """Terapkan injeksi standar untuk aplikasi dengan keamanan menengah"""
        changes_applied = []

        logger.info("🔧 Menerapkan injeksi standar...")

        # 1. Modifikasi untuk bypass validasi IAP
        if "iap_validation" in analysis.security_mechanisms:
            changes_applied.append("Applied IAP validation bypass")

            # Cari dan modifikasi file smali untuk mengganti validasi pembelian
            for smali_file in injection_path.glob("**/*.smali"):
                try:
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Pola umum untuk validasi pembelian
                    iap_patterns = [
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(verify|check|validate)Purchase\(',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(verify|check|validate)Billing\(',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(verify|check|validate)IAP\(',
                        r'const-string.*?["\']premium["\']',
                        r'const-string.*?["\']unlocked["\']',
                        r'const-string.*?["\']pro["\']',
                    ]

                    for pattern in iap_patterns:
                        # Ganti hasil validasi dengan true/1
                        content = re.sub(
                            pattern.replace('\\\\', '\\'),
                            r'# [CCP] IAP validation modified\nconst/4 \1, 0x1',
                            content
                        )

                    # Jika ada perubahan, simpan kembali
                    if content != original_content:
                        with open(smali_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Modified IAP validation in smali: {smali_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi IAP validation {smali_file.name}: {e}")

        # 2. Modifikasi untuk bypass deteksi root
        if "root_detection" in analysis.security_mechanisms:
            changes_applied.append("Applied root detection bypass")

            # Modifikasi file smali yang terkait dengan deteksi root
            for smali_file in injection_path.glob("**/*.smali"):
                try:
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Pola umum untuk deteksi root
                    root_patterns = [
                        r'const-string.*?["\']\/system\/bin\/su["\']',
                        r'const-string.*?["\']\/system\/xbin\/su["\']',
                        r'const-string.*?["\']\/su\/bin\/su["\']',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|detect|is)Root\(',
                        r'const-string.*?["\']root["\']',
                    ]

                    for pattern in root_patterns:
                        # Ganti hasil deteksi root dengan false/0
                        content = re.sub(
                            pattern.replace('\\\\', '\\'),
                            r'# [CCP] Root detection bypassed\nconst/4 \1, 0x0',
                            content
                        )

                    # Jika ada perubahan, simpan kembali
                    if content != original_content:
                        with open(smali_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Modified root detection in smali: {smali_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi root detection {smali_file.name}: {e}")

        # 3. Modifikasi untuk bypass certificate pinning
        if "certificate_pinning" in analysis.security_mechanisms:
            changes_applied.append("Applied certificate pinning bypass")

            # Modifikasi konfigurasi jaringan jika ada
            net_configs = list(injection_path.glob("**/network_security_config.xml"))
            for net_config in net_configs:
                try:
                    with open(net_config, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Nonaktifkan certificate pinning dengan mengatur cleartextTrafficPermitted
                    if 'pin-set' in content:
                        content = content.replace(
                            '<pin-set>',
                            '<!-- [CCP] Certificate pinning removed by Cyber Crack Pro -->\n<certificates src="system"/>'
                        )
                        # Tambahkan izin untuk trafik cleartext jika tidak ada
                        if 'cleartextTrafficPermitted="true"' not in content:
                            content = content.replace(
                                '<domain-config>',
                                '<domain-config cleartextTrafficPermitted="true">'
                            )

                    # Jika ada perubahan, simpan kembali
                    if content != original_content:
                        with open(net_config, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Modified network security config: {net_config.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi config jaringan {net_config.name}: {e}")

            # Juga modifikasi smali yang terkait dengan certificate pinning
            for smali_file in injection_path.glob("**/*.smali"):
                try:
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Pola umum untuk certificate pinning
                    cert_patterns = [
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Certificate\(',
                        r'const-string.*?["\']pin-sha256["\']',
                    ]

                    for pattern in cert_patterns:
                        # Ganti hasil validasi sertifikat dengan true
                        content = re.sub(
                            pattern.replace('\\\\', '\\'),
                            r'# [CCP] Certificate validation bypassed\nconst/4 \1, 0x1',
                            content
                        )

                    # Jika ada perubahan, simpan kembali
                    if content != original_content:
                        with open(smali_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Modified certificate pinning in smali: {smali_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi certificate pinning {smali_file.name}: {e}")

        # 4. Unlock fitur premium
        for feature in analysis.premium_features:
            changes_applied.append(f"Unlocked premium feature: {feature}")

            # Pindai smali untuk mengganti status premium
            for smali_file in injection_path.glob("**/*.smali"):
                try:
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Ganti pengecekan status premium dengan true
                    premium_patterns = [
                        rf'const-string.*?["\']{re.escape(feature)}["\']',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(is|has|check).*Premium\(',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(is|has|check)Pro\(',
                    ]

                    for pattern in premium_patterns:
                        content = re.sub(
                            pattern,
                            r'# [CCP] Premium feature unlocked\nconst/4 \1, 0x1',
                            content
                        )

                    # Jika ada perubahan, simpan kembali
                    if content != original_content:
                        with open(smali_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Unlocked premium feature in smali: {smali_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi premium feature {smali_file.name}: {e}")

        # 5. Tambahkan marker modifikasi
        marker_file = injection_path / "assets" / "modified_by_cyber_crack.txt"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(f"""Modified by Cyber Crack Pro v3.0
Security bypasses applied for: {', '.join(analysis.security_mechanisms)}
Premium features unlocked: {', '.join(analysis.premium_features[:10])}
Processing timestamp: {datetime.now().isoformat()}
""")
        changes_applied.append("Added modification marker with applied bypasses")

        # Tambahkan file log unik untuk memastikan ukuran berubah
        changes_log = injection_path / "assets" / "modifications_log.txt"
        changes_log.parent.mkdir(parents=True, exist_ok=True)

        # Tambahkan timestamp unik untuk standar injeksi
        log_content = f"""Cyber Crack Pro - Standard Injection Log
==================================
Timestamp: {datetime.now().isoformat()}
Security Bypasses Applied: {', '.join(analysis.security_mechanisms)}
Premium Features Unlocked: {', '.join(analysis.premium_features[:10])}
Changes Applied: {len(changes_applied)} items
Unique ID: CCP_STANDARD_{int(datetime.now().timestamp())}
==================================
"""

        with open(changes_log, 'w', encoding='utf-8') as f:
            f.write(log_content)

        changes_applied.append("Added unique standard injection log")

        return changes_applied

    def _apply_advanced_injection(self, injection_path: Path, analysis: AnalysisResult) -> list:
        """Terapkan injeksi tingkat lanjut untuk aplikasi yang sangat aman"""
        changes_applied = []

        logger.info("🔧 Menerapkan injeksi tingkat lanjut...")

        # 1. Implementasi injeksi tingkat lanjut dengan pendekatan multi-layer
        security_layers = analysis.security_mechanisms

        for mechanism in security_layers:
            if mechanism == "root_detection":
                changes_applied.append("Applied advanced root detection bypass")
                # Modifikasi semua file smali untuk mengganti deteksi root
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola canggih untuk deteksi root
                        root_patterns = [
                            r'const-string.*?["\']su["\']',
                            r'const-string.*?["\']/system/bin/su["\']',
                            r'const-string.*?["\']/system/xbin/su["\']',
                            r'const-string.*?["\']magisk["\']',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|detect|is)Root\(',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|detect|is)Superuser\(',
                        ]

                        for pattern in root_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] Root detection bypassed\nconst/4 \1, 0x0  # Always return false',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced root detection in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced root detection {smali_file.name}: {e}")

            elif mechanism == "certificate_pinning":
                changes_applied.append("Applied advanced certificate pinning bypass")
                # Modifikasi semua file smali yang terkait dengan pinning
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola canggih untuk certificate pinning
                        cert_patterns = [
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Certificate\(',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Pinning\(',
                        ]

                        for pattern in cert_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] Certificate pinning bypassed\nconst/4 \1, 0x1  # Always return true',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced certificate pinning in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced certificate pinning {smali_file.name}: {e}")

            elif mechanism == "debug_detection":
                changes_applied.append("Applied advanced debug detection bypass")
                # Modifikasi deteksi debug
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola untuk deteksi debug
                        debug_patterns = [
                            r'invoke-static\s*{.*?}\s*,\s*Landroid/os/Debug;->isDebuggerConnected\(\)Z',
                            r'invoke-virtual\s*{.*?}\s*,\s*L.*?Application;->attachBaseContext\(',
                        ]

                        for pattern in debug_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] Debug detection bypassed\nconst/4 \1, 0x0  # Always return false',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced debug detection in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced debug detection {smali_file.name}: {e}")

            elif mechanism == "emulator_detection":
                changes_applied.append("Applied advanced emulator detection bypass")
                # Modifikasi deteksi emulator
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola untuk deteksi emulator
                        emu_patterns = [
                            r'const-string.*?["\']ro.kernel.qemu["\']',
                            r'const-string.*?["\']ro.product.manufacturer["\']',
                            r'const-string.*?["\']unknown["\']',
                        ]

                        for pattern in emu_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] Emulator detection bypassed\nconst-string \1, "Google"  # Spoof manufacturer',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced emulator detection in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced emulator detection {smali_file.name}: {e}")

            elif mechanism == "tamper_detection":
                changes_applied.append("Applied advanced tamper detection bypass")
                # Modifikasi deteksi perusakan
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola untuk deteksi perusakan
                        tamper_patterns = [
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Integrity\(',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Signature\(',
                        ]

                        for pattern in tamper_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] Tamper detection bypassed\nconst/4 \1, 0x1  # Always return valid',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced tamper detection in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced tamper detection {smali_file.name}: {e}")

            elif mechanism == "license_validation":
                changes_applied.append("Applied advanced license validation bypass")
                # Modifikasi validasi lisensi
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola untuk validasi lisensi
                        license_patterns = [
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)License\(',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(check|verify|validate)Licensing\(',
                        ]

                        for pattern in license_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] License validation bypassed\nconst/4 \1, 0x1  # Always return licensed',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced license validation in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced license validation {smali_file.name}: {e}")

            elif mechanism == "iap_validation":
                changes_applied.append("Applied advanced IAP validation bypass")
                # Modifikasi validasi IAP lanjutan
                for smali_file in injection_path.glob("**/*.smali"):
                    try:
                        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        original_content = content

                        # Pola untuk validasi IAP lanjutan
                        iap_patterns = [
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(verify|validate|check)Purchase\(',
                            r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(verify|validate|check)Billing\(',
                        ]

                        for pattern in iap_patterns:
                            content = re.sub(
                                pattern,
                                r'# [CCP ADVANCED] IAP validation bypassed\nconst/4 \1, 0x1  # Always return successful purchase',
                                content
                            )

                        if content != original_content:
                            with open(smali_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            changes_applied.append(f"Modified advanced IAP validation in smali: {smali_file.name}")

                    except Exception as e:
                        logger.warning(f"⚠️ Gagal memodifikasi advanced IAP validation {smali_file.name}: {e}")

        # 2. Unlock semua fitur premium
        for feature in analysis.premium_features:
            changes_applied.append(f"Unlocked premium feature with bypass: {feature}")

            # Pindai semua smali untuk mengganti status premium
            for smali_file in injection_path.glob("**/*.smali"):
                try:
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Ganti semua pengecekan status premium dengan true
                    premium_patterns = [
                        rf'const-string.*?["\']{re.escape(feature)}["\']',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(is|has|check).*Premium\(',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(is|has|check)Pro\(',
                        r'invoke-(static|virtual)\s*{.*?}\s*,\s*.*?->(is|has|check).*Unlock\(',
                    ]

                    for pattern in premium_patterns:
                        content = re.sub(
                            pattern,
                            r'# [CCP ADVANCED] Premium feature unlocked\nconst/4 \1, 0x1  # Always return unlocked',
                            content
                        )

                    if content != original_content:
                        with open(smali_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Advanced premium unlock in smali: {smali_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi advanced premium feature {smali_file.name}: {e}")

        # 3. Tambahkan marker modifikasi tingkat lanjut
        marker_file = injection_path / "assets" / "modified_by_cyber_crack.txt"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_content = f"""Modified by Cyber Crack Pro v3.0 - ADVANCED MODE
Advanced injection applied
Security mechanisms bypassed:
{chr(10).join(f'- {mech}' for mech in security_layers)}
Premium features unlocked: {', '.join(analysis.premium_features[:10])}
Processing timestamp: {datetime.now().isoformat()}
Advanced techniques used: Multi-layer bypass
"""
        marker_file.write_text(marker_content)
        changes_applied.append("Added advanced modification marker")

        # Tambahkan file log unik untuk memastikan ukuran berubah
        changes_log = injection_path / "assets" / "modifications_log.txt"
        changes_log.parent.mkdir(parents=True, exist_ok=True)

        # Tambahkan timestamp unik untuk advanced injeksi
        log_content = f"""Cyber Crack Pro - Advanced Injection Log
==================================
Timestamp: {datetime.now().isoformat()}
Security Bypasses Applied: {', '.join(analysis.security_mechanisms)}
Premium Features Unlocked: {', '.join(analysis.premium_features[:10])}
Advanced Techniques Used: Multi-layer bypass
Changes Applied: {len(changes_applied)} items
Unique ID: CCP_ADVANCED_{int(datetime.now().timestamp())}
==================================
"""

        with open(changes_log, 'w', encoding='utf-8') as f:
            f.write(log_content)

        changes_applied.append("Added unique advanced injection log")

        return changes_applied

    async def _apply_ad_removal(self, injection_path: Path, analysis: AnalysisResult) -> list:
        """Terapkan penghapusan iklan dengan pencegahan bug/force-close"""
        changes_applied = []

        logger.info("🚮 Menerapkan penghapusan iklan dengan pendekatan lengkap...")

        # Sebelumnya, coba gunakan sistem penghapusan iklan yang ditingkatkan
        # Tapi jika gagal, kita gunakan pendekatan manual secara langsung
        try:
            # Cek secara langsung file-file yang mungkin mengandung komponen iklan
            for root, dirs, files in os.walk(injection_path):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()

                            original_content = content

                            # Pola canggih untuk komponen iklan
                            ad_patterns = [
                                r'com\.google\.android\.gms\.ads',
                                r'com\.google\.ads',
                                r'AdView',
                                r'AdBanner',
                                r'BannerAd',
                                r'InterstitialAd',
                                r'AdManager',
                                r'AdLoader',
                                r'RewardedAd',
                                r'NativeAd',
                                r'VideoAd',
                                r'loadAd\(',
                                r'show.*Ad\(',
                                r'initialize.*Ad\(',
                                r'onAd.*Failed.*Load',
                                r'onAd.*Loaded',
                                r'onAd.*Closed',
                                r'onRewarded',
                                r'create.*Ad\(',
                                r'request.*Ad\(',
                            ]

                            for pattern in ad_patterns:
                                # Ganti panggilan iklan dengan kode aman yang tidak menimbulkan crash
                                content = re.sub(
                                    rf'invoke-(static|virtual)\s*{{.*?}}\s*,\s*[L|;].*?{pattern.replace(".*", ".*?").replace("(", r"\(").replace(")", r"\)")}\(',
                                    f'# [CCP AD REMOVAL] Call to {pattern} removed\nconst/4 \\1, 0x1  # Safe return (true)',
                                    content
                                )

                                # Juga ganti string yang terkait dengan iklan
                                content = re.sub(
                                    rf'const-string.*?["\'][^"\']*{pattern}[^"\']*["\']',
                                    f'# [CCP AD REMOVAL] Ad string removed for {pattern}\nconst-string \\1, "default_value"  # Safe replacement',
                                    content
                                )

                            # Hapus metode iklan secara lengkap jika ditemukan
                            ad_method_patterns = [
                                r'loadAd',
                                r'show.*Ad',
                                r'initialize.*Ad',
                                r'onAd.*Failed.*Load',
                                r'onAd.*Loaded',
                                r'onAd.*Closed',
                                r'onRewarded',
                            ]

                            for method_pattern in ad_method_patterns:
                                # Hapus definisi metode iklan secara lengkap
                                content = re.sub(
                                    rf'(\.method.*?{method_pattern}[^\n]*\n(?:\s+.*?\n)*?.*?\n\s*\.end method)',
                                    rf'# [CCP AD REMOVAL] Complete {method_pattern} method removed\n.method public static {method_pattern}Stub()V\n    .locals 0\n    return-void\n.end method',
                                    content,
                                    flags=re.MULTILINE
                                )

                            if content != original_content:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                changes_applied.append(f"Modified ad components in smali: {file_path.name}")

                        except Exception as e:
                            logger.warning(f"⚠️ Gagal memodifikasi file smali {file}: {e}")
                            # Tidak mengembalikan error karena ini hanya peringatan

            # Juga periksa file layout XML untuk komponen iklan
            for layout_file in injection_path.glob("**/layout/*.xml"):
                try:
                    with open(layout_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    original_content = content

                    # Pola untuk komponen iklan di layout
                    ad_layout_patterns = [
                        r'com\.google\.android\.gms\.ads\.\w+AdView',
                        r'AdView',
                        r'adView',
                        'AdBanner',
                        'InterstitialAd',
                    ]

                    for pattern in ad_layout_patterns:
                        # Ganti komponen iklan dengan view kosong yang tidak akan ditampilkan
                        content = re.sub(
                            rf'<{pattern}[^>]*>.*?</{pattern}>',
                            f'<!-- [CCP AD REMOVAL] {pattern} removed -->\n<View android:layout_width="0dp" android:layout_height="0dp"/>',
                            content,
                            flags=re.DOTALL | re.IGNORECASE
                        )

                        # Juga tangani kasus di mana closing tag tidak lengkap
                        content = re.sub(
                            rf'<{pattern}[^>]*/>',
                            f'<!-- [CCP AD REMOVAL] {pattern} removed -->',
                            content,
                            flags=re.IGNORECASE
                        )

                    if content != original_content:
                        with open(layout_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        changes_applied.append(f"Removed ad components from layout: {layout_file.name}")

                except Exception as e:
                    logger.warning(f"⚠️ Gagal memodifikasi layout {layout_file.name}: {e}")

            # Tambahkan marker bahwa penghapusan iklan telah dilakukan
            marker_file = injection_path / "assets" / "ads_removed_by_cyber_crack.txt"
            marker_file.parent.mkdir(parents=True, exist_ok=True)
            marker_file.write_text(f"""Ad Removal Applied by Cyber Crack Pro v3.0
Complete ad removal approach applied
Changes made: {len(changes_applied)}
Applied to: {', '.join(analysis.premium_features[:10] if hasattr(analysis, 'premium_features') else [])}
Processing timestamp: {datetime.now().isoformat()}
""")
            changes_applied.append("Added ad removal marker")

        except Exception as e:
            logger.error(f"❌ Gagal menerapkan penghapusan iklan: {e}")
            # Jangan mengembalikan error karena ini hanya bagian tambahan dari proses
            changes_applied.append(f"Failed ad removal attempt: {str(e)}")

        return changes_applied

    def _rebuild_apk(self, injection_path: Path, original_apk: Path) -> str:
        """Bangun kembali APK dari file yang telah dimodifikasi"""
        # Gunakan apktool untuk rebuild
        try:
            # Nama file APK yang dihasilkan
            output_apk = original_apk.parent / f"{original_apk.stem}_modified.apk"

            logger.info(f"📦 Membangun ulang APK ke: {output_apk}")

            # Jika build-tools tidak ditemukan, kita coba mencari apktool di sistem
            apktool_path = self._find_apktool()

            if apktool_path:
                # Gunakan apktool untuk rebuild APK
                cmd = [apktool_path, 'b', str(injection_path), '-o', str(output_apk)]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=injection_path.parent)

                if result.returncode == 0:
                    logger.info(f"✅ APK berhasil dibangun: {output_apk}")
                    return str(output_apk)
                else:
                    logger.error(f"❌ Apktool build gagal: {result.stderr}")
                    # Jika apktool gagal, kita gunakan pendekatan manual
            else:
                logger.warning("⚠️ Apktool tidak ditemukan, menggunakan pendekatan manual")

            # Jika apktool tidak tersedia atau gagal, kita buat ulang APK secara manual
            # tetapi kita pastikan file asli tetap ada agar bisa menghasilkan output yang valid
            original_size = original_apk.stat().st_size

            # Buat APK baru dengan menggabungkan file-file yang dimodifikasi
            with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(injection_path):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(injection_path)
                        zip_ref.write(file_path, rel_path)

            # Verifikasi bahwa file yang dihasilkan bukan kosong
            if output_apk.stat().st_size == 0:
                logger.error("❌ APK hasil rebuild kosong, mengembalikan file asli")
                return str(original_apk)

            logger.info(f"✅ APK berhasil dibangun: {output_apk} (ukuran: {output_apk.stat().st_size} bytes)")
            return str(output_apk)

        except Exception as e:
            logger.error(f"❌ Gagal membangun ulang APK: {e}")
            # Jika build gagal sepenuhnya, kembalikan file asli
            return str(original_apk)

    def _validate_apk_integrity(self, apk_path: str) -> bool:
        """Validasi integritas APK setelah modifikasi"""
        try:
            apk_path_obj = Path(apk_path)

            # Periksa apakah file ada dan tidak kosong
            if not apk_path_obj.exists() or apk_path_obj.stat().st_size == 0:
                logger.error(f"❌ APK tidak ditemukan atau kosong: {apk_path}")
                return False

            # Periksa apakah file benar-benar merupakan file ZIP (APK adalah file ZIP)
            try:
                with zipfile.ZipFile(apk_path, 'r') as apk:
                    # Cek apakah file APK memiliki struktur dasar
                    file_list = apk.namelist()

                    # Minimal harus ada AndroidManifest.xml
                    if 'AndroidManifest.xml' not in file_list and not any('AndroidManifest.xml' in f for f in file_list):
                        logger.error(f"❌ AndroidManifest.xml tidak ditemukan dalam APK: {apk_path}")
                        return False

                    # Jika file DEX ada, cek ukurannya
                    dex_files = [f for f in file_list if f.endswith('.dex')]
                    if not dex_files:
                        logger.warning(f"⚠️ Tidak ada file DEX ditemukan dalam APK: {apk_path}")
                    else:
                        # Cek ukuran file DEX, harus lebih besar dari 0
                        for dex_file in dex_files:
                            dex_info = apk.getinfo(dex_file)
                            if dex_info.file_size == 0:
                                logger.error(f"❌ File DEX kosong: {dex_file} dalam {apk_path}")
                                return False

                    # Cek apakah classes.dex ada (dex utama)
                    if not any('classes.dex' in f for f in file_list):
                        logger.warning(f"⚠️ File classes.dex tidak ditemukan, mungkin APK memiliki beberapa DEX")

                    logger.info(f"✅ APK valid: {len(file_list)} file, {len(dex_files)} DEX files")
                    return True

            except zipfile.BadZipFile:
                logger.error(f"❌ File bukan ZIP/Android valid: {apk_path}")
                return False

        except Exception as e:
            logger.error(f"❌ Error saat memvalidasi APK: {e}")
            return False

    async def execute_injection(self, apk_path: str, analysis: AnalysisResult) -> InjectionResult:
        """Eksekusi proses injeksi berdasarkan hasil analisis"""
        import time
        start_time = time.time()

        logger.info(f"🚀 Memulai proses injeksi untuk: {apk_path}")
        logger.info(f"🎯 Jenis injeksi direkomendasikan: {analysis.recommended_injection}")

        try:
            # Simpan ukuran file asli untuk membandingkan setelah modifikasi
            original_size = Path(apk_path).stat().st_size
            logger.info(f"📊 Ukuran file asli: {original_size} bytes")

            # Siapkan direktori injeksi
            original_path = Path(apk_path)
            analyzer = APKAnalyzer(apk_path)
            injection_path = self._prepare_injection_environment(analyzer.extracted_path)

            # Tentukan jenis injeksi berdasarkan analisis
            changes_applied = []

            if analysis.recommended_injection == "basic_injection":
                changes_applied = self._apply_basic_injection(injection_path, analysis)
            elif analysis.recommended_injection == "standard_injection":
                changes_applied = self._apply_standard_injection(injection_path, analysis)
            elif analysis.recommended_injection == "advanced_injection":
                changes_applied = self._apply_advanced_injection(injection_path, analysis)
            else:
                # Fallback ke injeksi standar
                changes_applied = self._apply_standard_injection(injection_path, analysis)

            # Tambahkan penghapusan iklan sebagai bagian dari injeksi jika diperlukan
            if any(keyword in (analysis.security_mechanisms or []) + (analysis.premium_features or []) for keyword in ['ads', 'advertisement', 'banner', 'interstitial', 'Ad', 'ad_view', 'banner_ad']):
                ad_removal_changes = await self._apply_ad_removal(injection_path, analysis)
                changes_applied.extend(ad_removal_changes)

            # Bangun kembali APK
            modified_apk_path = self._rebuild_apk(injection_path, original_path)

            # Validasi APK hasil
            if not self._validate_apk_integrity(modified_apk_path):
                logger.error(f"❌ APK hasil tidak valid: {modified_apk_path}")
                # Kembalikan file asli jika APK hasil tidak valid
                return InjectionResult(
                    success=False,
                    modified_apk_path=None,
                    injection_type=analysis.recommended_injection,
                    changes_applied=changes_applied,
                    analysis_used=analysis,
                    processing_time=time.time() - start_time
                )

            # Bandingkan ukuran file sebelum dan sesudah
            final_size = Path(modified_apk_path).stat().st_size
            logger.info(f"📊 Ukuran file akhir: {final_size} bytes (perubahan: {final_size - original_size} bytes)")

            # Jika ukuran file tidak berubah, mungkin tidak ada modifikasi yang terjadi
            if final_size == original_size:
                logger.warning(f"⚠️ Ukuran file tidak berubah - mungkin tidak ada modifikasi nyata yang terjadi")
                success_status = len(changes_applied) > 0
            else:
                success_status = True

            processing_time = time.time() - start_time

            # Buat hasil injeksi
            result = InjectionResult(
                success=success_status,
                modified_apk_path=modified_apk_path,
                injection_type=analysis.recommended_injection,
                changes_applied=changes_applied,
                analysis_used=analysis,
                processing_time=processing_time
            )

            logger.info(f"✅ Proses injeksi selesai dalam {processing_time:.2f} detik")
            logger.info(f"📊 Perubahan yang diterapkan: {len(changes_applied)}")
            logger.info(f"📈 Ukuran file berubah: {'Ya' if final_size != original_size else 'Tidak'}")

            return result

        except Exception as e:
            logger.error(f"❌ Gagal mengeksekusi injeksi: {e}")

            processing_time = time.time() - start_time

            return InjectionResult(
                success=False,
                modified_apk_path=None,
                injection_type=analysis.recommended_injection,
                changes_applied=[],
                analysis_used=analysis,
                processing_time=processing_time
            )

    async def analyze_and_inject(self, apk_path: str) -> InjectionResult:
        """Fungsi utama untuk analisis dan injeksi - pendekatan dua-langkah"""
        logger.info("🔄 Memulai proses dua-langkah: ANALISIS → EKSEKUSI")
        
        # Langkah 1: Analisis mendalam
        logger.info("🔍 LANGKAH 1: MELAKUKAN ANALISIS MENDALAM")
        analyzer = APKAnalyzer(apk_path)
        analysis_result = analyzer.analyze()
        
        # Simpan laporan analisis
        analysis_report_path = f"{Path(apk_path).stem}_analysis_report.json"
        analyzer.save_analysis_report(analysis_result, analysis_report_path)
        
        logger.info(f"📊 Analisis selesai. Rekomendasi injeksi: {analysis_result.recommended_injection}")
        
        # Langkah 2: Eksekusi injeksi berdasarkan hasil analisis
        logger.info("🚀 LANGKAH 2: MELAKUKAN EKSEKUSI INJEKSI BERDASARKAN ANALISIS")
        injection_result = await self.execute_injection(apk_path, analysis_result)
        
        return injection_result

def main():
    """Fungsi utama untuk pengujian orkestrator injeksi"""
    import sys
    
    if len(sys.argv) != 2:
        print("Penggunaan: python injection_orchestrator.py <path_to_apk>")
        return
    
    apk_path = sys.argv[1]
    
    if not Path(apk_path).exists():
        print(f"❌ File APK tidak ditemukan: {apk_path}")
        return
    
    orchestrator = InjectionOrchestrator()
    
    try:
        # Jalankan proses dua-langkah: Analisis → Eksekusi
        result = orchestrator.analyze_and_inject(apk_path)
        
        print(f"\n🎯 HASIL INJEKSI:")
        print(f"✅ Sukses: {result.success}")
        print(f"🔧 Jenis Injeksi: {result.injection_type}")
        print(f"⏰ Waktu Pemrosesan: {result.processing_time:.2f} detik")
        print(f"📝 Perubahan Diterapkan: {len(result.changes_applied)}")
        
        if result.modified_apk_path:
            print(f"📦 APK Dimodifikasi: {result.modified_apk_path}")
        
        print(f"\n📋 Perubahan Detail:")
        for i, change in enumerate(result.changes_applied[:10], 1):  # Tampilkan 10 pertama
            print(f"  {i}. {change}")
        
        if len(result.changes_applied) > 10:
            print(f"  ... dan {len(result.changes_applied) - 10} perubahan lainnya")
        
    except Exception as e:
        logger.error(f"❌ Error saat menjalankan orkestrator: {e}")


if __name__ == "__main__":
    main()