#!/bin/bash
# 🚀 CYBER CRACK PRO v3.0 - CLEANUP & OPTIMIZATION SCRIPT
# Menghapus file-file tidak penting dan mengatur sistem yang optimal

echo "🧹 CLEANING UP UNNECESSARY FILES..."
echo "================================="

# File-file tidak penting untuk dihapus
find . -type f -name "*.log" ! -name "bot.log" -delete
find . -type f -name "*.tmp" -delete
find . -type f -name "*.bak" -delete
find . -type f -name "*.old" -delete
find . -type f -name "*backup*" -delete
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete

# Hapus file dokumentasi duplikat
find . -name "*IMPLEMENTATION*.md" -not -name "FINAL_IMPLEMENTATION_COMPLETE.md" -delete
find . -name "*FINAL*.md" -not -name "FINAL_IMPLEMENTATION_COMPLETE.md" -delete
find . -name "*STATUS*.md" -not -name "FINAL_STATUS.md" -delete
find . -name "*COMPLETE*.md" -not -name "FINAL_IMPLEMENTATION_COMPLETE.md" -delete
find . -name "*SUMMARY*.md" -not -name "SUMMARY.md" -delete

# Hapus script-test tidak perlu
find . -name "*test*.py" -not -name "test_bot.py" -delete
find . -name "*demo*.py" -not -name "run_bot.py" -delete

# Hapus direktori sementara
rm -rf temp/ testing/ testing_results/ backups/ temp_* logs/*

echo "✅ Cleanup completed!"
echo ""
echo "🗂️ CREATING ESSENTIAL DIRECTORY STRUCTURE..."
mkdir -p uploads results logs temp
echo "📁 uploads/, results/, logs/, temp/ directories created"
echo ""
echo "🔧 SYSTEM OPTIMIZATION COMPLETE!"
echo "💡 Essential files remaining for operation:"
ls -la backend_api.py web_dashboard.py complete_telegram_bot.py apk_analyzer.py injection_orchestrator.py 2>/dev/null || echo "Files may have different names, showing all Python files:"
find . -maxdepth 1 -name "*.py" -type f | head -10