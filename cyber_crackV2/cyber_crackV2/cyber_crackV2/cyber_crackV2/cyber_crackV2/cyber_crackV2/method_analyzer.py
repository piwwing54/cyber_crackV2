#!/usr/bin/env python3
"""
🔍 CYBER CRACK PRO v3.0 - METHOD ANALYZER
Sistem analisis dan modifikasi method dalam file DEX
"""

import asyncio
import os
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple
import zipfile
from datetime import datetime

class MethodAnalyzer:
    """Analisis dan modifikasi method dalam file DEX"""
    
    def __init__(self, extracted_dir: Path):
        self.extracted_dir = extracted_dir
        self.dex_files = list(extracted_dir.glob("**/*.dex"))
        self.smali_files = list(extracted_dir.glob("**/*.smali"))
        
        # Daftar method umum yang sering dimodifikasi
        self.target_methods = {
            'security_checks': [
                'isRooted', 'checkRoot', 'isDeviceRooted', 'isDebugged', 'isDebuggerConnected',
                'checkTrustZone', 'verifySignature', 'checkLicense', 'validatePurchase',
                'isNetworkSecure', 'verifyCert', 'pinningCheck', 'isEmulator'
            ],
            'iap_validation': [
                'isPurchased', 'isPremium', 'isUnlocked', 'validateReceipt', 'checkBilling',
                'isBillingSupported', 'getPurchasedItems', 'verifyPayment'
            ],
            'feature_unlocks': [
                'isPro', 'isPremium', 'isUnlocked', 'hasFullAccess', 'isTrialExpired',
                'requireSubscription', 'showAds', 'isAdFree'
            ]
        }
        
    async def analyze_methods(self) -> Dict[str, List[Dict]]:
        """Analisis semua method dalam DEX dan Smali files"""
        print(f"[{datetime.now().strftime('%H.%M.%S')}] 🔍 Analyzing methods in DEX files...")
        
        analysis_results = {
            'dex_methods_count': 0,
            'smali_methods_count': 0,
            'target_methods_found': {
                'security_checks': [],
                'iap_validation': [],
                'feature_unlocks': []
            },
            'all_methods': []
        }
        
        # Analisis file Smali untuk mendapatkan informasi method
        for smali_file in self.smali_files:
            methods_in_file = await self._analyze_smali_file(smali_file)
            
            analysis_results['smali_methods_count'] += len(methods_in_file)
            analysis_results['all_methods'].extend(methods_in_file)
            
            # Cek apakah method cocok dengan target
            for method in methods_in_file:
                for category, target_list in self.target_methods.items():
                    for target in target_list:
                        if target.lower() in method['name'].lower():
                            analysis_results['target_methods_found'][category].append({
                                'method': method,
                                'file': str(smali_file.relative_to(self.extracted_dir))
                            })
        
        print(f"[{datetime.now().strftime('%H.%M.%S')}] 📊 Found {analysis_results['smali_methods_count']} methods across {len(self.smali_files)} Smali files")
        
        # Tampilkan temuan target methods
        for category, methods in analysis_results['target_methods_found'].items():
            if methods:
                print(f"[{datetime.now().strftime('%H.%M.%S')}] 🎯 Found {len(methods)} {category} methods")
        
        return analysis_results
    
    async def _analyze_smali_file(self, smali_file: Path) -> List[Dict]:
        """Analisis file Smali untuk menemukan method-method"""
        methods = []
        
        try:
            content = smali_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            current_method = None
            current_class = ""
            
            for line in lines:
                line = line.strip()
                
                # Cek apakah ini definisi class
                if line.startswith('.class'):
                    # Ambil nama class dari akhir baris
                    parts = line.split()
                    if len(parts) > 1:
                        current_class = parts[-1]
                
                # Cek apakah ini definisi method
                elif line.startswith('.method'):
                    # Ekstrak nama method
                    method_sig = line.replace('.method', '').strip()
                    method_name = self._extract_method_name(method_sig)
                    
                    if method_name:
                        current_method = {
                            'name': method_name,
                            'signature': method_sig,
                            'class': current_class,
                            'file': str(smali_file.relative_to(self.extracted_dir)),
                            'line_start': lines.index(line) + 1 if line in lines else 0
                        }
                        methods.append(current_method)
                
                # Cek akhir method
                elif line.startswith('.end method') and current_method:
                    current_method = None
        
        except Exception as e:
            print(f"[{datetime.now().strftime('%H.%M.%S')}] ⚠️ Error analyzing Smali file {smali_file}: {str(e)}")
        
        return methods
    
    def _extract_method_name(self, method_signature: str) -> str:
        """Ekstrak nama method dari signature"""
        # Format umum: [access] [type] method_name(parameters)return_type
        # Contoh: public final synthetic a(Ljava/lang/Object;)Ljava/lang/Object;
        
        # Cari nama method antara spasi dan tanda kurung
        parts = method_signature.split('(')
        if len(parts) > 0:
            name_part = parts[0].split()  # Pisahkan access modifiers
            if len(name_part) > 0:
                # Ambil bagian terakhir sebagai nama
                return name_part[-1].split('/')[-1]  # Hapus path kelas jika ada
        
        # Jika format tidak terdeteksi, kembalikan signature utuh
        return method_signature
    
    async def modify_methods(self, target_methods: List[Dict], modification_type: str = "bypass"):
        """Modifikasi method-method target dengan injeksi bypass"""
        print(f"[{datetime.now().strftime('%H.%M.%S')}] 🔧 Modifying {len(target_methods)} methods with {modification_type} injection")
        
        modified_count = 0
        modifications_log = []
        
        for target in target_methods:
            method_info = target['method']
            file_path = self.extracted_dir / target['file']
            
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Tergantung jenis modifikasi, lakukan injeksi yang sesuai
                modified_content = self._apply_modification(content, method_info, modification_type)
                
                if content != modified_content:
                    file_path.write_text(modified_content, encoding='utf-8')
                    modified_count += 1
                    
                    modifications_log.append({
                        'method': method_info['name'],
                        'file': target['file'],
                        'modification': modification_type
                    })
                    
                    print(f"[{datetime.now().strftime('%H.%M.%S')}] ✅ Modified: {method_info['name']} in {target['file']}")
            
            except Exception as e:
                print(f"[{datetime.now().strftime('%H.%M.%S')}] ❌ Failed to modify {method_info['name']}: {str(e)}")
        
        print(f"[{datetime.now().strftime('%H.%M.%S')}] ✅ Successfully modified {modified_count} methods")
        return modifications_log
    
    def _apply_modification(self, content: str, method_info: Dict, modification_type: str) -> str:
        """Menerapkan modifikasi ke konten file Smali"""
        # Cari definisi method dan tambahkan instruksi bypass
        method_start = f".method {method_info['signature']}"
        
        if method_start in content:
            # Temukan method dan tambahkan return true (untuk bypass)
            if modification_type == "bypass":
                # Ganti baris pertama setelah .method dengan return true
                lines = content.split('\n')
                new_lines = []
                
                in_target_method = False
                method_processed = False
                
                for line in lines:
                    if line.strip().startswith('.method') and method_info['name'] in line:
                        in_target_method = True
                        new_lines.append(line)
                    elif in_target_method and not method_processed and line.strip() == '':
                        # Tambahkan bypass setelah baris kosong pertama dalam method
                        new_lines.extend([
                            '    .locals 1',
                            '    const/4 v0, 0x1',  # Set result to true
                            '    return v0',        # Return true
                        ])
                        method_processed = True
                        in_target_method = False
                    elif in_target_method and line.strip().startswith('.end method'):
                        # Jika method sudah diproses, jangan tambahkan lagi
                        if method_processed:
                            in_target_method = False
                        new_lines.append(line)
                    elif in_target_method and method_processed:
                        # Lewatkan baris lain dalam method yang sudah diproses
                        continue
                    else:
                        if line.strip().startswith('.end method'):
                            in_target_method = False
                        new_lines.append(line)
                
                return '\n'.join(new_lines)
        
        return content  # Jika tidak ditemukan perubahan, kembalikan konten asli


class AdvancedMethodInjector:
    """Sistem injeksi method tingkat lanjut"""
    
    def __init__(self, extracted_dir: Path):
        self.extracted_dir = extracted_dir
        self.method_analyzer = MethodAnalyzer(extracted_dir)
    
    async def run_advanced_analysis_injection(self) -> Dict:
        """Jalankan analisis dan injeksi method tingkat lanjut"""
        print(f"[{datetime.now().strftime('%H.%M.%S')}] 🚀 Starting Advanced Method Analysis & Injection")
        
        # Analisis semua method
        analysis_results = await self.method_analyzer.analyze_methods()
        
        # Gabungkan semua target method dari berbagai kategori
        all_target_methods = []
        for category, methods in analysis_results['target_methods_found'].items():
            all_target_methods.extend(methods)
        
        if all_target_methods:
            print(f"[{datetime.now().strftime('%H.%M.%S')}] 💉 Found {len(all_target_methods)} target methods for injection")
            
            # Terapkan modifikasi bypass ke semua target method
            modifications = await self.method_analyzer.modify_methods(all_target_methods, "bypass")
            
            print(f"[{datetime.now().strftime('%H.%M.%S')}] ✅ Advanced method injection completed")
            
            analysis_results['applied_modifications'] = modifications
        else:
            print(f"[{datetime.now().strftime('%H.%M.%S')}] ℹ️ No specific target methods found, applying general patches")
            
            # Jika tidak ada target method spesifik, aplikasikan patch umum
            all_methods = analysis_results['all_methods']
            general_targets = [m for m in all_methods if any(keyword in m['name'].lower() 
                                                           for keyword in ['check', 'validate', 'verify', 'is', 'has'])]
            
            if general_targets:
                general_method_targets = [{'method': m, 'file': m['file']} for m in general_targets[:10]]  # Batasi 10
                modifications = await self.method_analyzer.modify_methods(general_method_targets, "bypass")
                analysis_results['applied_modifications'] = modifications
                print(f"[{datetime.now().strftime('%H.%M.%S')}] 💉 Applied general bypass to {len(modifications)} methods")
        
        analysis_results['status'] = 'completed'
        analysis_results['timestamp'] = datetime.now().isoformat()
        
        return analysis_results