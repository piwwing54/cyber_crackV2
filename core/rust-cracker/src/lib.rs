pub mod analyzer;
pub mod crack_engine;
pub mod pattern_matcher;
pub mod apk_processor;
pub mod network_security;
pub mod anti_debug;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub use analyzer::*;
pub use crack_engine::*;
pub use pattern_matcher::*;
pub use apk_processor::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct APKAnalysis {
    pub apk_path: String,
    pub package_name: String,
    pub version: String,
    pub vulnerabilities: Vec<Vulnerability>,
    pub protections: Vec<Protection>,
    pub security_score: u8,
    pub recommendations: Vec<String>,
    pub complexity_level: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Vulnerability {
    pub id: String,
    pub name: String,
    pub description: String,
    pub severity: String,  // CRITICAL, HIGH, MEDIUM, LOW
    pub location: String,
    pub code_snippet: String,
    pub confidence: f64,
    pub fix_suggestion: String,
    pub exploit_code: Option<String>,
    pub cvss_score: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Protection {
    pub id: String,
    pub name: String,
    pub description: String,
    pub type_field: String,  // root_detection, cert_pinning, etc.
    pub strength: String,    // STRONG, MEDIUM, WEAK
    pub bypass_method: String,
    pub location: String,
    pub isActive: bool,
    pub dependencies: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrackResult {
    pub success: bool,
    pub modified_apk_path: String,
    pub fixes_applied: Vec<String>,
    pub vulnerabilities_found: usize,
    pub protections_identified: usize,
    pub stability_score: u8,
    pub processing_time_ms: u128,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrackRequest {
    pub apk_path: String,
    pub category: Option<String>,
    pub features: Option<Vec<String>>,
    pub options: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrackResponse {
    pub success: bool,
    pub message: String,
    pub modified_apk_path: Option<String>,
    pub fixes_applied: Vec<String>,
    pub vulnerabilities_found: usize,
    pub protections_identified: usize,
    pub error: Option<String>,
    pub processing_time_ms: u128,
}

// Type aliases for convenience
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
pub type ByteCode = Vec<u8>;
pub type Patch = (usize, Vec<u8>); // (offset, new_bytes)