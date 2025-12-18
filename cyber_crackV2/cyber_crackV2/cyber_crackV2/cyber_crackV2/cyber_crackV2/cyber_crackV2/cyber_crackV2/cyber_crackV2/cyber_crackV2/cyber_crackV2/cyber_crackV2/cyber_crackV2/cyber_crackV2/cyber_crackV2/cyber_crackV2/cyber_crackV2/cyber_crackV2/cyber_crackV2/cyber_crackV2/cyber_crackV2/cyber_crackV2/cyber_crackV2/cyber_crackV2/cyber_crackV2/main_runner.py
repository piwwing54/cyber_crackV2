#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - MAIN RUNNER
Sistem integrasi lengkap: ANALYSIS → EXECUTION
Menggabungkan semua komponen sistem untuk operasi penuh
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Tambahkan path ke direktori project agar bisa mengimpor modul
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Periksa apakah semua modul dependensi tersedia"""
    required_modules = [
        "aiogram",
        "apk_analyzer",
        "injection_orchestrator"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == "aiogram":
                import aiogram
            elif module == "apk_analyzer":
                from apk_analyzer import APKAnalyzer
            elif module == "injection_orchestrator":
                from injection_orchestrator import InjectionOrchestrator
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.warning(f"Modul berikut tidak ditemukan: {missing_modules}")
        logger.info("Beberapa fitur mungkin terbatas, tetapi sistem tetap akan berfungsi")
        return False
    else:
        logger.info("✅ Semua modul dependensi tersedia")
        return True

def create_uploads_directory():
    """Buat direktori uploads jika belum ada"""
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    logger.info(f"📁 Direktori uploads siap: {uploads_dir.absolute()}")

def main():
    """Fungsi utama untuk menjalankan sistem lengkap"""
    print("🚀 CYBER CRACK PRO v3.0 - MAIN RUNNER")
    print("=====================================")
    print("Sistem Analisis-Sebelum-Eksekusi (Analysis-Before-Execution)")
    print("Menggabungkan: APK Analyzer + Injection Orchestrator + Telegram Bot")
    print()
    
    # Periksa dependensi
    dependencies_ok = check_dependencies()
    
    # Buat direktori uploads
    create_uploads_directory()
    
    # Mulai sistem bot
    print("🔧 Memulai sistem Telegram Bot...")
    
    try:
        # Impor dan jalankan bot
        from simple_telegram_bot import main as bot_main
        print("✅ Sistem bot siap")
        print("🔗 Menunggu pesan dari Telegram...")
        print()
        print("📋 PERINTAH YANG TERSEDIA:")
        print("   /start    - Mulai bot dan tampilkan menu")
        print("   /crack    - Mode modifikasi APK")
        print("   /help     - Bantuan dan perintah")
        print("   /status   - Status sistem")
        print()
        print("💡 CARA PENGGUNAAN:")
        print("   1. Kirim perintah /start")
        print("   2. Unggah file APK (.apk)")
        print("   3. Sistem akan menganalisis secara menyeluruh")
        print("   4. Pilih opsi modifikasi dari menu")
        print("   5. Tunggu proses selesai dan download hasilnya")
        print()
        
        # Jalankan bot
        asyncio.run(bot_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan oleh pengguna")
    except Exception as e:
        logger.error(f"❌ Error saat menjalankan sistem: {e}")
        import traceback
        traceback.print_exc()

def run_analysis_only(apk_path: str = None):
    """Fungsi untuk menjalankan hanya analisis jika path APK diberikan"""
    if not apk_path:
        print("Menjalankan mode interaktif...")
        return main()
    
    apk_path = Path(apk_path)
    if not apk_path.exists():
        print(f"❌ File APK tidak ditemukan: {apk_path}")
        return
    
    try:
        from apk_analyzer import APKAnalyzer
        print(f"🔍 Menganalisis APK: {apk_path.name}")
        
        analyzer = APKAnalyzer(str(apk_path))
        analysis_result = analyzer.analyze()
        
        print(f"\n📊 HASIL ANALISIS untuk: {apk_path.name}")
        print(f"🛡️ Mekanisme Keamanan: {len(analysis_result.security_mechanisms)}")
        print(f"💎 Fitur Premium: {len(analysis_result.premium_features)}")
        print(f"⚙️ Rekomendasi Injeksi: {analysis_result.recommended_injection}")
        print(f"📋 DEX Files: {len(analysis_result.app_structure.get('dex_files', []))}")
        print(f"🔐 Perlindungan Total: {sum(analysis_result.protection_levels.values())}")
        print(f"🔑 Permissions: {len(analysis_result.permissions)}")
        
        # Simpan laporan
        report_path = f"{apk_path.stem}_analysis_report.json"
        analyzer.save_analysis_report(analysis_result, report_path)
        print(f"📁 Laporan disimpan ke: {report_path}")
        
    except Exception as e:
        print(f"❌ Error saat menganalisis APK: {e}")

def run_analysis_and_injection(apk_path: str = None):
    """Fungsi untuk menjalankan analisis dan injeksi penuh"""
    if not apk_path:
        print("Menjalankan mode interaktif...")
        return main()
    
    apk_path = Path(apk_path)
    if not apk_path.exists():
        print(f"❌ File APK tidak ditemukan: {apk_path}")
        return
    
    try:
        from injection_orchestrator import InjectionOrchestrator
        print(f"🚀 Menjalankan proses Analisis→Injeksi untuk: {apk_path.name}")
        
        orchestrator = InjectionOrchestrator()
        result = orchestrator.analyze_and_inject(str(apk_path))
        
        print(f"\n🎯 HASIL INJEKSI untuk: {apk_path.name}")
        print(f"✅ Sukses: {result.success}")
        print(f"🔧 Jenis Injeksi: {result.injection_type}")
        print(f"⏰ Waktu Pemrosesan: {result.processing_time:.2f} detik")
        print(f"📝 Perubahan Diterapkan: {len(result.changes_applied)}")
        
        if result.modified_apk_path:
            print(f"📦 APK Hasil: {result.modified_apk_path}")
        
        print(f"\n📋 Rincian Perubahan:")
        for i, change in enumerate(result.changes_applied[:10], 1):  # Tampilkan 10 pertama
            print(f"  {i}. {change}")
        
        if len(result.changes_applied) > 10:
            print(f"  ... dan {len(result.changes_applied) - 10} perubahan lainnya")
            
    except Exception as e:
        print(f"❌ Error saat menjalankan analisis dan injeksi: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Jalankan mode bot penuh
        main()
    elif len(sys.argv) == 2:
        # Jalankan mode analisis saja
        run_analysis_only(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[1] == "--inject":
        # Jalankan mode analisis + injeksi
        run_analysis_and_injection(sys.argv[2])
    else:
        print("Penggunaan:")
        print("  python main_runner.py                    # Jalankan bot Telegram penuh")
        print("  python main_runner.py <path_to_apk>      # Analisis APK")
        print("  python main_runner.py --inject <path_to_apk>  # Analisis dan injeksi APK")