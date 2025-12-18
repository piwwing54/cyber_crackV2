use std::collections::HashMap;
use std::fs;
use std::path::Path;
use regex::Regex;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use tokio;

use crate::{APKAnalysis, Vulnerability, Protection};

pub struct NetworkSecurityAnalyzer {
    cert_pinning_patterns: Vec<String>,
    insecure_communication_patterns: Vec<String>,
    hardcoded_endpoint_patterns: Vec<String>,
    ssl_validation_bypass_patterns: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityFinding {
    pub id: String,
    pub name: String,
    pub description: String,
    pub severity: String,  // CRITICAL, HIGH, MEDIUM, LOW
    pub location: String,
    pub code_snippet: String,
    pub confidence: f64,
    pub fix_suggestion: String,
    pub exploit_code: Option<String>,
}

impl NetworkSecurityAnalyzer {
    pub fn new() -> Self {
        Self {
            cert_pinning_patterns: vec![
                r"(CertificatePinner|pin\(|pinRecord|checkServerTrusted|X509TrustManager)".to_string(),
                r"(networkSecurityConfig|securityConfig|certificates|pin-set)".to_string(),
                r"(getTrustManagers|getPinnedCertificates|pinningAlgorithm)".to_string(),
            ],
            insecure_communication_patterns: vec![
                r"http://".to_string(),
                r"(setAllowAllHostnameVerifier|ALLOW_ALL_HOSTNAME|VerifiesNone)".to_string(),
                r"(SSLSocketFactory|SSLContext|TrustManagerFactory)".to_string(),
            ],
            hardcoded_endpoint_patterns: vec![
                r"(https?://[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,})".to_string(),
                r"(API_URL|BASE_URL|SERVER_ENDPOINT)".to_string(),
                r"(endpoint|url|host|server)".to_string(),
            ],
            ssl_validation_bypass_patterns: vec![
                r"(checkServerTrusted.*|verify.*X509|validate.*ssl|verify.*hostname)".to_string(),
                r"(isSslError|sslErrorHandler|handleSslError)".to_string(),
                r"(acceptAllCerts|allowAllCerts|trustAllCerts)".to_string(),
            ],
        }
    }
    
    pub async fn analyze_network_security(&self, extracted_path: &str) -> Result<(Vec<Vulnerability>, Vec<Protection>)> {
        let mut vulnerabilities = Vec::new();
        let mut protections = Vec::new();
        
        // Search for network security issues in smali files
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)
                .with_context(|| format!("Failed to read smali file: {}", smali_file.display()))?;
            
            // Check for certificate pinning implementations
            for pattern in &self.cert_pinning_patterns {
                let re = Regex::new(pattern)?;
                
                for (line_num, line) in content.lines().enumerate() {
                    if re.is_match(line) {
                        // This is a protection if it's implemented to enhance security
                        if self.is_protection_implementation(line) {
                            let protection = Protection {
                                id: format!("cert_pinning_{}", smali_file.file_name().unwrap_or_default().to_string_lossy()),
                                name: "Certificate Pinning".to_string(),
                                description: format!("Certificate pinning detected in {}", smali_file.display()),
                                type_field: "certificate_pinning".to_string(),
                                strength: "HIGH".to_string(),
                                bypass_method: "Implement TrustManager bypass".to_string(),
                                location: format!("{}:{}", smali_file.display(), line_num + 1),
                                is_active: true,
                                dependencies: vec!["ssl_context_manipulation".to_string()],
                            };
                            protections.push(protection);
                        } else {
                            // Otherwise, it might be a vulnerability if improperly implemented
                            let vuln = Vulnerability {
                                id: format!("cert_pinning_vuln_{}", smali_file.file_name().unwrap_or_default().to_string_lossy()),
                                name: "Weak Certificate Pinning".to_string(),
                                description: format!("Improperly implemented certificate pinning in {}", smali_file.display()),
                                severity: "MEDIUM".to_string(),
                                location: format!("{}:{}", smali_file.display(), line_num + 1),
                                code_snippet: line.trim().to_string(),
                                confidence: 0.75,
                                fix_suggestion: "Strengthen certificate pinning implementation".to_string(),
                                exploit_code: Some("// Bypass certificate pinning".to_string()),
                                cvss_score: Some(6.5),
                            };
                            vulnerabilities.push(vuln);
                        }
                    }
                }
            }
            
            // Check for insecure communication
            for pattern in &self.insecure_communication_patterns {
                let re = Regex::new(pattern)?;
                
                for (line_num, line) in content.lines().enumerate() {
                    if re.is_match(line) && !self.is_comment(line) {
                        let vuln = Vulnerability {
                            id: format!("insecure_comm_{}", smali_file.file_name().unwrap_or_default().to_string_lossy()),
                            name: "Insecure Communication".to_string(),
                            description: format!("Insecure network communication detected in {}", smali_file.display()),
                            severity: if pattern.contains("http://") { "HIGH" } else { "MEDIUM" }.to_string(),
                            location: format!("{}:{}", smali_file.display(), line_num + 1),
                            code_snippet: line.trim().to_string(),
                            confidence: 0.9,
                            fix_suggestion: "Use HTTPS for all communications".to_string(),
                            exploit_code: Some("// Intercept sensitive data in transit".to_string()),
                            cvss_score: if pattern.contains("http://") { Some(7.5) } else { Some(5.3) },
                        };
                        vulnerabilities.push(vuln);
                    }
                }
            }
            
            // Check for hardcoded endpoints
            for pattern in &self.hardcoded_endpoint_patterns {
                let re = Regex::new(pattern)?;
                
                for (line_num, line) in content.lines().enumerate() {
                    if re.is_match(line) && !self.is_assignment_to_config_variable(line) {
                        let vuln = Vulnerability {
                            id: format!("hardcoded_endpoint_{}", smali_file.file_name().unwrap_or_default().to_string_lossy()),
                            name: "Hardcoded Endpoint".to_string(),
                            description: format!("Hardcoded server endpoint detected in {}", smali_file.display()),
                            severity: "MEDIUM".to_string(),
                            location: format!("{}:{}", smali_file.display(), line_num + 1),
                            code_snippet: line.trim().to_string(),
                            confidence: 0.85,
                            fix_suggestion: "Parameterize server endpoints".to_string(),
                            exploit_code: Some("// Identify API endpoints for analysis".to_string()),
                            cvss_score: Some(5.3),
                        };
                        vulnerabilities.push(vuln);
                    }
                }
            }
            
            // Check for SSL validation bypass opportunities
            for pattern in &self.ssl_validation_bypass_patterns {
                let re = Regex::new(pattern)?;
                
                for (line_num, line) in content.lines().enumerate() {
                    if re.is_match(line) {
                        if self.looks_like_bypass_implementation(line) {
                            let vuln = Vulnerability {
                                id: format!("ssl_bypass_{}", smali_file.file_name().unwrap_or_default().to_string_lossy()),
                                name: "SSL Validation Bypass Opportunity".to_string(),
                                description: format!("SSL validation bypass opportunity in {}", smali_file.display()),
                                severity: "HIGH".to_string(),
                                location: format!("{}:{}", smali_file.display(), line_num + 1),
                                code_snippet: line.trim().to_string(),
                                confidence: 0.92,
                                fix_suggestion: "Implement proper SSL validation".to_string(),
                                exploit_code: Some("// Bypass SSL validation".to_string()),
                                cvss_score: Some(8.1),
                            };
                            vulnerabilities.push(vuln);
                        }
                    }
                }
            }
        }
        
        // Also check manifest for network security configuration
        let manifest_path = Path::new(extracted_path).join("AndroidManifest.xml");
        if manifest_path.exists() {
            let manifest_content = fs::read_to_string(&manifest_path)?;
            
            if manifest_content.contains("android:networkSecurityConfig") {
                let vuln = Vulnerability {
                    id: "network_security_config".to_string(),
                    name: "Custom Network Security Configuration".to_string(),
                    description: "Custom network security configuration found in manifest".to_string(),
                    severity: "MEDIUM".to_string(),
                    location: format!("{}", manifest_path.display()),
                    code_snippet: "android:networkSecurityConfig".to_string(),
                    confidence: 0.8,
                    fix_suggestion: "Analyze custom security configuration".to_string(),
                    exploit_code: Some("// Review custom network security config".to_string()),
                    cvss_score: Some(4.8),
                };
                
                vulnerabilities.push(vuln);
            }
        }
        
        Ok((vulnerabilities, protections))
    }
    
    fn is_protection_implementation(&self, line: &str) -> bool {
        // Determine if the code line represents a security protection implementation
        let lower_line = line.to_lowercase();
        
        lower_line.contains("check") || 
        lower_line.contains("verify") || 
        lower_line.contains("validate") || 
        lower_line.contains("secure") || 
        lower_line.contains("trust") || 
        lower_line.contains("certificate") || 
        lower_line.contains("pin") ||
        lower_line.contains("auth") || 
        lower_line.contains("protect")
    }
    
    fn is_comment(&self, line: &str) -> bool {
        line.trim_start().starts_with("#") || 
        line.trim_start().starts_with("//") ||
        line.trim_start().starts_with("/*") ||
        line.trim_start().starts_with("*")
    }
    
    fn is_assignment_to_config_variable(&self, line: &str) -> bool {
        // Check if line is an assignment to a configuration variable (less critical)
        let lower_line = line.to_lowercase();
        lower_line.contains("config") || 
        lower_line.contains("settings") || 
        lower_line.contains("preferences") ||
        lower_line.contains("const")
    }
    
    fn looks_like_bypass_implementation(&self, line: &str) -> bool {
        // Check if the line looks like it's implementing a bypass rather than protection
        let lower_line = line.to_lowercase();
        
        lower_line.contains("bypass") || 
        lower_line.contains("disable") || 
        lower_line.contains("remove") ||
        lower_line.contains("skip") || 
        lower_line.contains("null") || 
        lower_line.contains("always_true") ||
        lower_line.contains("false")
    }
    
    async fn find_files_by_extension(&self, directory: &str, extension: &str) -> Result<Vec<std::path::PathBuf>> {
        let mut files = Vec::new();
        
        for entry in walkdir::WalkDir::new(directory) {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() && path.extension().map_or(false, |ext| ext == extension) {
                files.push(path.to_path_buf());
            }
        }
        
        Ok(files)
    }
    
    pub async fn bypass_certificate_pinning(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut bypasses_applied = Vec::new();
        
        // Look for certificate pinning implementations
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)
                .with_context(|| format!("Failed to read smali file: {}", smali_file.display()))?;
            
            let mut modified_content = content.clone();
            let mut found_cert_pinning = false;
            
            // Look for certificate pinning implementations
            for pattern in &self.cert_pinning_patterns {
                let re = Regex::new(pattern)?;
                
                for line in modified_content.lines() {
                    if re.is_match(line) && self.is_cert_pinning_check_method(line) {
                        // Replace verification with always-return-true
                        if line.contains("->checkServerTrusted") || line.contains("->verify") {
                            // Find the method boundary and replace validation logic
                            let method_pattern = format!(
                                r#"(.method.*{}.*\n.*?)\n.end method"#,
                                regex::escape(line.split_whitespace().last().unwrap_or(""))
                            );
                            
                            if let Ok(method_re) = Regex::new(&method_pattern) {
                                modified_content = method_re.replace_all(&modified_content, |caps: &regex::Captures| {
                                    let method = &caps[1];
                                    // Replace method implementation with always return true
                                    format!("{}\n    const/4 v0, 0x1\n    return v0\n.end method", 
                                        method.lines().take_while(|&l| !l.starts_with("return")).collect::<Vec<_>>().join("\n"))
                                }).to_string();
                                
                                found_cert_pinning = true;
                            }
                        }
                    }
                }
            }
            
            if found_cert_pinning {
                fs::write(&smali_file, &modified_content)
                    .with_context(|| format!("Failed to write modified smali file: {}", smali_file.display()))?;
                
                bypasses_applied.push(format!("Applied certificate pinning bypass to: {}", smali_file.display()));
            }
        }
        
        Ok(bypasses_applied)
    }
    
    fn is_cert_pinning_check_method(&self, line: &str) -> bool {
        // Check if the line is part of a certificate pinning validation method
        let lower_line = line.to_lowercase();
        lower_line.contains("checkserver") || 
        lower_line.contains("cert") || 
        lower_line.contains("pin") || 
        lower_line.contains("trust") ||
        lower_line.contains("validat")
    }
    
    pub async fn bypass_ssl_validation(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut bypasses_applied = Vec::new();
        
        // Similar to cert pinning bypass, but for SSL validation
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)
                .with_context(|| format!("Failed to read smali file: {}", smali_file.display()))?;
            
            let mut modified_content = content.clone();
            let mut found_ssl_validation = false;
            
            // Look for SSL validation implementations
            for pattern in &self.ssl_validation_bypass_patterns {
                let re = Regex::new(pattern)?;
                
                for line in modified_content.lines() {
                    if re.is_match(line) && self.is_ssl_validation_method(line) {
                        // Replace validation with always-return-success
                        if line.contains("verify") || line.contains("validate") {
                            // This is a simplified implementation - a real one would need to parse the method properly
                            let new_method = format!(
                                "{}\n    # SSL validation bypassed by Cyber Crack Pro\n    const/4 v0, 0x1\n    return v0",
                                line
                            );
                            modified_content = modified_content.replace(line, &new_method);
                            found_ssl_validation = true;
                        }
                    }
                }
            }
            
            if found_ssl_validation {
                fs::write(&smali_file, &modified_content)
                    .with_context(|| format!("Failed to write modified smali file: {}", smali_file.display()))?;
                
                bypasses_applied.push(format!("Applied SSL validation bypass to: {}", smali_file.display()));
            }
        }
        
        Ok(bypasses_applied)
    }
    
    fn is_ssl_validation_method(&self, line: &str) -> bool {
        let lower_line = line.to_lowercase();
        lower_line.contains("ssl") || 
        lower_line.contains("https") || 
        lower_line.contains("validate") || 
        lower_line.contains("verify") ||
        lower_line.contains("hostname")
    }
    
    pub async fn patch_hardcoded_endpoints(&self, extracted_path: &str, new_endpoint: &str) -> Result<Vec<String>> {
        let mut patches_applied = Vec::new();
        
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)
                .with_context(|| format!("Failed to read smali file: {}", smali_file.display()))?;
            
            let mut modified_content = content.clone();
            let mut found_hardcoded = false;
            
            // Look for hardcoded endpoints
            for pattern in &self.hardcoded_endpoint_patterns {
                let re = Regex::new(pattern)?;
                
                for line in modified_content.lines() {
                    if re.is_match(line) && !self.is_assignment_to_config_variable(line) {
                        // Replace hardcoded endpoint with new one
                        modified_content = modified_content.replace(
                            &line.trim(),
                            &format!("    # Patched by Cyber Crack Pro - Original: {}\n    const-string {}, \"{}\"", 
                                   line.trim(), 
                                   self.extract_string_register(line)?,
                                   new_endpoint)
                        );
                        found_hardcoded = true;
                    }
                }
            }
            
            if found_hardcoded {
                fs::write(&smali_file, &modified_content)
                    .with_context(|| format!("Failed to write modified smali file: {}", smali_file.display()))?;
                
                patches_applied.push(format!("Patched hardcoded endpoints in: {}", smali_file.display()));
            }
        }
        
        Ok(patches_applied)
    }
    
    fn extract_string_register(&self, line: &str) -> Result<String> {
        // Extract the register from a const-string instruction
        // Pattern: const-string v0, "original_url"
        let re = Regex::new(r"const-string\s+(v\d+),")
            .with_context(|| "Failed to compile register extraction regex")?;
        
        if let Some(caps) = re.captures(line) {
            Ok(caps[1].to_string())
        } else {
            // If no register found in const-string, return a default
            Ok("v0".to_string())
        }
    }
    
    pub async fn analyze_network_security_config(&self, extracted_path: &str) -> Result<Vec<SecurityFinding>> {
        let mut findings = Vec::new();
        
        // Check for network_security_config.xml
        let net_sec_config_path = Path::new(extracted_path).join("res/xml/network_security_config.xml");
        if net_sec_config_path.exists() {
            let content = fs::read_to_string(&net_sec_config_path)?;
            
            // Check for cleartext traffic permit
            if content.contains("<base-config cleartextTrafficPermitted=\"true\">") {
                let finding = SecurityFinding {
                    id: "cleartext_traffic_permitted".to_string(),
                    name: "Cleartext Traffic Permitted".to_string(),
                    description: "Network security config allows cleartext traffic".to_string(),
                    severity: "HIGH".to_string(),
                    location: format!("{}", net_sec_config_path.display()),
                    code_snippet: "<base-config cleartextTrafficPermitted=\"true\">".to_string(),
                    confidence: 1.0,
                    fix_suggestion: "Disallow cleartext traffic in network security config".to_string(),
                    exploit_code: Some("// Exploit allows HTTP traffic interception".to_string()),
                };
                
                findings.push(finding);
            }
            
            // Check for certificate pinning bypass
            if content.contains("<certificates src=\"system\" overridePins=\"true\"/>") {
                let finding = SecurityFinding {
                    id: "cert_override_enabled".to_string(),
                    name: "Certificate Override Enabled".to_string(),
                    description: "Network security config overrides certificate pins".to_string(),
                    severity: "HIGH".to_string(),
                    location: format!("{}", net_sec_config_path.display()),
                    code_snippet: "<certificates src=\"system\" overridePins=\"true\"/>".to_string(),
                    confidence: 1.0,
                    fix_suggestion: "Disable certificate override in network security config".to_string(),
                    exploit_code: Some("// Bypass certificate pinning using config".to_string()),
                };
                
                findings.push(finding);
            }
        }
        
        Ok(findings)
    }
}

// Additional helper functions for network security analysis
impl NetworkSecurityAnalyzer {
    pub async fn identify_secure_endpoints(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut secure_endpoints = Vec::new();
        
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            // Look for HTTPS endpoints
            let https_regex = Regex::new(r"https://[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}").unwrap();
            
            for cap in https_regex.captures_iter(&content) {
                let endpoint = cap.get(0).unwrap().as_str();
                if !secure_endpoints.contains(&endpoint.to_string()) {
                    secure_endpoints.push(endpoint.to_string());
                }
            }
        }
        
        Ok(secure_endpoints)
    }
    
    pub async fn identify_insecure_endpoints(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut insecure_endpoints = Vec::new();
        
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            // Look for HTTP endpoints
            let http_regex = Regex::new(r"http://[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}").unwrap();
            
            for cap in http_regex.captures_iter(&content) {
                let endpoint = cap.get(0).unwrap().as_str();
                if !insecure_endpoints.contains(&endpoint.to_string()) {
                    insecure_endpoints.push(endpoint.to_string());
                }
            }
        }
        
        Ok(insecure_endpoints)
    }
    
    pub async fn find_debug_endpoints(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut debug_endpoints = Vec::new();
        
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            // Look for potential debug/test endpoints
            let debug_regex = Regex::new(r"(?i)(debug|test|staging|dev)\.(server|api|endpoint)").unwrap();
            
            for cap in debug_regex.captures_iter(&content) {
                let endpoint = cap.get(0).unwrap().as_str();
                if !debug_endpoints.contains(&endpoint.to_string()) {
                    debug_endpoints.push(endpoint.to_string());
                }
            }
        }
        
        Ok(debug_endpoints)
    }
    
    pub async fn find_api_key_locations(&self, extracted_path: &str) -> Result<Vec<String>> {
        let mut api_key_locations = Vec::new();
        
        let smali_files = self.find_files_by_extension(extracted_path, ".smali").await?;
        
        for smali_file in smali_files {
            let content = fs::read_to_string(&smali_file)?;
            
            // Look for potential API key patterns
            let api_key_regex = Regex::new(r#"(?i)("apiKey"|"api_key"|"key"|"token"|"secret").*(".*")"#).unwrap();
            
            for cap in api_key_regex.captures_iter(&content) {
                if cap.len() >= 3 {
                    let key = cap.get(1).unwrap().as_str();
                    let value = cap.get(2).unwrap().as_str();
                    
                    // Check if the value is long enough to be an actual API key
                    if value.len() > 30 {
                        api_key_locations.push(format!(
                            "{}:{} - {} = {}",
                            smali_file.display(),
                            content.match_indices(value).next().map(|(i, _)| content[..i].matches('\n').count() + 1).unwrap_or(0),
                            key,
                            value
                        ));
                    }
                }
            }
        }
        
        Ok(api_key_locations)
    }
}