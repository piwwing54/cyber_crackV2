use std::fs;
use std::path::Path;
use regex::Regex;
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};

use crate::{APKAnalysis, Vulnerability, Protection};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AntiDebugFinding {
    pub id: String,
    pub name: String,
    pub description: String,
    pub severity: String,
    pub location: String,
    pub code_snippet: String,
    pub confidence: f64,
    pub fix_suggestion: String,
    pub bypass_method: String,
}

pub struct AntiDebugAnalyzer {
    debug_detection_patterns: Vec<String>,
    emulator_detection_patterns: Vec<String>,
    anti_vm_patterns: Vec<String>,
    integrity_check_patterns: Vec<String>,
    dynamic_analysis_patterns: Vec<String>,
}

impl AntiDebugAnalyzer {
    pub fn new() -> Self {
        Self {
            debug_detection_patterns: vec![
                r"(isDebuggerConnected|waitUntilDebuggerAttached|checkDebugger|debug|Debug)".to_string(),
                r"(android:debuggable|BuildConfig\.DEBUG|DEBUG)".to_string(),
                r"(TracerPid|ro\.debuggable|ro\.secure|ro\.build\.tags)".to_string(),
            ],
            emulator_detection_patterns: vec![
                r"(ro\.product\.model|ro\.product\.manufacturer)".to_string(),
                r"(emulator|genymotion|bluestacks|x86|ro\.kernel|qemu)".to_string(),
                r"(goldfish|vbox|android|sdk|test-key)".to_string(),
            ],
            anti_vm_patterns: vec![
                r"(virtual|vm|hypervisor|qemu|bochs|virtualbox|vmware|parallels)".to_string(),
                r"(isVirtual|isVm|runningInVm|hypervisor|virtual_machine)".to_string(),
            ],
            integrity_check_patterns: vec![
                r"(signature|checksum|hash|verify|integrity|tamper|authenticity)".to_string(),
                r"(PackageManager|getSignatures|SIGNATURE_|signatureHash)".to_string(),
            ],
            dynamic_analysis_patterns: vec![
                r"(frida|hook|intercept|xposed|substrate|cydia|sosand)".to_string(),
                r"(objection|inspector|runtime|instrumentation|dynamic|analysis)".to_string(),
            ],
        }
    }
    
    pub async fn analyze_anti_debug(&self, extracted_path: &str) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        // Search in smali files
        let smali_files = self.find_smali_files(extracted_path).await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)
                .with_context(|| format!("Failed to read smali file: {}", smali_file.display()))?;
            
            // Check for debug detection
            let debug_findings = self.check_debug_detection(&content, &smali_file).await?;
            findings.extend(debug_findings);
            
            // Check for emulator detection
            let emulator_findings = self.check_emulator_detection(&content, &smali_file).await?;
            findings.extend(emulator_findings);
            
            // Check for anti-VM
            let vm_findings = self.check_anti_vm(&content, &smali_file).await?;
            findings.extend(vm_findings);
            
            // Check for integrity checks
            let integrity_findings = self.check_integrity_checks(&content, &smali_file).await?;
            findings.extend(integrity_findings);
        }
        
        // Check for manifest-based debug detection
        let manifest_path = Path::new(extracted_path).join("AndroidManifest.xml");
        if manifest_path.exists() {
            let manifest_content = fs::read_to_string(&manifest_path)?;
            let manifest_findings = self.check_manifest_debug_detection(&manifest_content, &manifest_path).await?;
            findings.extend(manifest_findings);
        }
        
        Ok(findings)
    }
    
    async fn check_debug_detection(&self, content: &str, file_path: &Path) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        for pattern in &self.debug_detection_patterns {
            let re = Regex::new(pattern)?;
            
            for (line_num, line) in content.lines().enumerate() {
                if re.is_match(line) && !self.is_comment(line) {
                    let finding = AntiDebugFinding {
                        id: format!("debug_{}", line_num),
                        name: "Debug Detection".to_string(),
                        description: "Potential debug detection mechanism".to_string(),
                        severity: "HIGH".to_string(),
                        location: format!("{}:{}", file_path.display(), line_num + 1),
                        code_snippet: line.trim().to_string(),
                        confidence: 0.9,
                        fix_suggestion: "Bypass debug detection checks".to_string(),
                        bypass_method: "Hook isDebuggerConnected() and related methods".to_string(),
                    };
                    
                    findings.push(finding);
                }
            }
        }
        
        Ok(findings)
    }
    
    async fn check_emulator_detection(&self, content: &str, file_path: &Path) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        for pattern in &self.emulator_detection_patterns {
            let re = Regex::new(pattern)?;
            
            for (line_num, line) in content.lines().enumerate() {
                if re.is_match(line) && !self.is_comment(line) {
                    let finding = AntiDebugFinding {
                        id: format!("emulator_{}", line_num),
                        name: "Emulator Detection".to_string(),
                        description: "Potential emulator detection mechanism".to_string(),
                        severity: "MEDIUM".to_string(),
                        location: format!("{}:{}", file_path.display(), line_num + 1),
                        code_snippet: line.trim().to_string(),
                        confidence: 0.85,
                        fix_suggestion: "Bypass emulator detection checks".to_string(),
                        bypass_method: "Modify device properties to appear as physical device".to_string(),
                    };
                    
                    findings.push(finding);
                }
            }
        }
        
        Ok(findings)
    }
    
    async fn check_anti_vm(&self, content: &str, file_path: &Path) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        for pattern in &self.anti_vm_patterns {
            let re = Regex::new(pattern)?;
            
            for (line_num, line) in content.lines().enumerate() {
                if re.is_match(line) && !self.is_comment(line) {
                    let finding = AntiDebugFinding {
                        id: format!("vm_{}", line_num),
                        name: "Virtual Machine Detection".to_string(),
                        description: "Potential virtual machine detection mechanism".to_string(),
                        severity: "MEDIUM".to_string(),
                        location: format!("{}:{}", file_path.display(), line_num + 1),
                        code_snippet: line.trim().to_string(),
                        confidence: 0.8,
                        fix_suggestion: "Bypass virtual machine detection".to_string(),
                        bypass_method: "Hide VM indicators and hypervisor bits".to_string(),
                    };
                    
                    findings.push(finding);
                }
            }
        }
        
        Ok(findings)
    }
    
    async fn check_integrity_checks(&self, content: &str, file_path: &Path) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        for pattern in &self.integrity_check_patterns {
            let re = Regex::new(pattern)?;
            
            for (line_num, line) in content.lines().enumerate() {
                if re.is_match(line) && !self.is_comment(line) {
                    let finding = AntiDebugFinding {
                        id: format!("integrity_{}", line_num),
                        name: "Integrity Check".to_string(),
                        description: "Potential app integrity check mechanism".to_string(),
                        severity: "MEDIUM".to_string(),
                        location: format!("{}:{}", file_path.display(), line_num + 1),
                        code_snippet: line.trim().to_string(),
                        confidence: 0.88,
                        fix_suggestion: "Bypass integrity verification".to_string(),
                        bypass_method: "Hook signature verification functions".to_string(),
                    };
                    
                    findings.push(finding);
                }
            }
        }
        
        Ok(findings)
    }
    
    async fn check_manifest_debug_detection(&self, content: &str, file_path: &Path) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        // Check for debuggable flag in manifest
        if content.contains("android:debuggable=\"true\"") {
            let finding = AntiDebugFinding {
                id: "manifest_debuggable".to_string(),
                name: "Debuggable Manifest Flag".to_string(),
                description: "Application is marked as debuggable in manifest".to_string(),
                severity: "LOW".to_string(),
                location: format!("{}", file_path.display()),
                code_snippet: "android:debuggable=\"true\"".to_string(),
                confidence: 1.0,
                fix_suggestion: "Remove debuggable flag in production".to_string(),
                bypass_method: "Flag indicates app is already debug-friendly".to_string(),
            };
            
            findings.push(finding);
        }
        
        Ok(findings)
    }
    
    async fn bypass_debug_detection(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut bypasses_applied = Vec::new();
        
        let smali_files = self.find_smali_files(extracted_path).await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            let mut modified_content = content.clone();
            let mut found_debug_check = false;
            
            // Look for debug detection functions and bypass them
            for pattern in &self.debug_detection_patterns {
                let re = Regex::new(pattern)?;
                
                for line in modified_content.lines() {
                    if re.is_match(line) && (line.contains("isDebugger") || line.contains("isDebug")) {
                        // If this is a method call that checks for debug, replace it to always return false
                        if line.contains("invoke") && line.contains("return") {
                            // Find the method and modify its return value
                            let method_pattern = Regex::new(r".method.*")?;
                            if let Some(method_start) = method_pattern.find(line) {
                                // Add code to force return of false/0
                                let forced_return = if line.contains("boolean") || line.contains("Z") {
                                    "    const/4 v0, 0x0\n    return v0\n"
                                } else {
                                    "    const/4 v0, 0x0\n    return v0\n"
                                };
                                
                                modified_content = modified_content.replace(
                                    line,
                                    &format!("{}# DEBUG CHECK BYPASSED\n{}", line, forced_return)
                                );
                                found_debug_check = true;
                            }
                        }
                    }
                }
            }
            
            if found_debug_check {
                fs::write(&smali_file, &modified_content)?;
                bypasses_applied.push(format!("Applied debug bypass to: {}", smali_file.display()));
            }
        }
        
        Ok(bypasses_applied)
    }
    
    async fn bypass_emulator_detection(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut bypasses_applied = Vec::new();
        
        let smali_files = self.find_smali_files(extracted_path).await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            let mut modified_content = content.clone();
            let mut found_emulator_check = false;
            
            // Look for emulator detection checks and bypass them
            for pattern in &self.emulator_detection_patterns {
                let re = Regex::new(pattern)?;
                
                for line in modified_content.lines() {
                    if re.is_match(line) && 
                       (line.contains("emulator") || 
                        line.contains("checkEmulator") || 
                        line.contains("isEmulator")) {
                        // Replace emulator check with always return false
                        modified_content = modified_content.replace(
                            line,
                            &format!("# EMULATOR CHECK BYPASSED\n{}    const/4 v0, 0x0\n    return v0", line)
                        );
                        found_emulator_check = true;
                    }
                }
            }
            
            if found_emulator_check {
                fs::write(&smali_file, &modified_content)?;
                bypasses_applied.push(format!("Applied emulator bypass to: {}", smali_file.display()));
            }
        }
        
        Ok(bypasses_applied)
    }
    
    fn is_comment(&self, line: &str) -> bool {
        line.trim_start().starts_with('#') || 
        line.trim_start().starts_with('"') ||  // Inside string
        line.contains("comment") || 
        line.to_lowercase().contains("todo") ||
        line.to_lowercase().contains("fixme")
    }
    
    async fn find_smali_files(&self, directory: &str) -> Result<Vec<std::path::PathBuf>> {
        let mut files = Vec::new();
        
        for entry in walkdir::WalkDir::new(directory) {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() && path.extension().map_or(false, |ext| ext == "smali") {
                files.push(path.to_path_buf());
            }
        }
        
        Ok(files)
    }
    
    pub async fn analyze_for_dynamic_tools(&self, extracted_path: &str) -> Result<Vec<AntiDebugFinding>> {
        let mut findings = Vec::new();
        
        let smali_files = self.find_smali_files(extracted_path).await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            for pattern in &self.dynamic_analysis_patterns {
                let re = Regex::new(pattern)?;
                
                for (line_num, line) in content.lines().enumerate() {
                    if re.is_match(line) && !self.is_comment(line) {
                        let finding = AntiDebugFinding {
                            id: format!("dynamic_analysis_{}", line_num),
                            name: "Dynamic Analysis Detection".to_string(),
                            description: "Potential detection of dynamic analysis tools".to_string(),
                            severity: "MEDIUM".to_string(),
                            location: format!("{}:{}", smali_file.display(), line_num + 1),
                            code_snippet: line.trim().to_string(),
                            confidence: 0.75,
                            fix_suggestion: "Bypass dynamic analysis detection".to_string(),
                            bypass_method: "Hook detection methods to return false".to_string(),
                        };
                        
                        findings.push(finding);
                    }
                }
            }
        }
        
        Ok(findings)
    }
    
    pub async fn bypass_all_detection(&self, extracted_path: &str) -> Result<BypassResult> {
        let mut total_bypasses = 0;
        let mut all_bypass_messages = Vec::new();
        
        // Apply all types of bypasses
        let debug_bypasses = self.bypass_debug_detection(extracted_path).await?;
        total_bypasses += debug_bypasses.len();
        all_bypass_messages.extend(debug_bypasses);
        
        let emulator_bypasses = self.bypass_emulator_detection(extracted_path).await?;
        total_bypasses += emulator_bypasses.len();
        all_bypass_messages.extend(emulator_bypasses);
        
        // Add more bypasses as needed
        
        Ok(BypassResult {
            total_bypasses_applied: total_bypasses,
            bypasses_applied: all_bypass_messages,
            success: total_bypasses > 0,
        })
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BypassResult {
    pub total_bypasses_applied: usize,
    pub bypasses_applied: Vec<String>,
    pub success: bool,
}