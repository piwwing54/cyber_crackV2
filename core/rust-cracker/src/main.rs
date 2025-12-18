use std::env;
use std::fs;
use std::path::Path;
use std::process;

mod cracker;
mod binary_patcher;
mod pattern_matcher;
mod memory_manager;

use cracker::{RustCracker, AnalysisResult};
use binary_patcher::BinaryPatcher;
use pattern_matcher::{PatternMatcher, PatternAnalysisResult};
use memory_manager::MemoryManager;
use serde_json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize memory manager
    let memory_manager = memory_manager::MemoryManager::new();
    
    // Parse command line arguments
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: {} <command> [options]", args[0]);
        eprintln!("Commands:");
        eprintln!("  analyze <apk_path>          - Analyze an APK for vulnerabilities");
        eprintln!("  process <apk_path> <mode>   - Process/modify an APK");
        eprintln!("  patch <apk_path> <type>     - Apply a specific patch to an APK");
        eprintln!("  patterns <text>             - Find patterns in text");
        process::exit(1);
    }
    
    let command = &args[1];
    
    match command.as_str() {
        "analyze" => {
            if args.len() < 3 {
                eprintln!("Usage: {} analyze <apk_path>", args[0]);
                process::exit(1);
            }
            
            let apk_path = &args[2];
            perform_analysis(apk_path).await?;
        }
        
        "process" => {
            if args.len() < 4 {
                eprintln!("Usage: {} process <apk_path> <mode>", args[0]);
                process::exit(1);
            }
            
            let apk_path = &args[2];
            let mode = &args[3];
            perform_processing(apk_path, mode).await?;
        }
        
        "patch" => {
            if args.len() < 4 {
                eprintln!("Usage: {} patch <apk_path> <patch_type>", args[0]);
                process::exit(1);
            }
            
            let apk_path = &args[2];
            let patch_type = &args[3];
            perform_patching(apk_path, patch_type)?;
        }
        
        "patterns" => {
            if args.len() < 3 {
                eprintln!("Usage: {} patterns <text_to_analyze>", args[0]);
                process::exit(1);
            }
            
            let text = &args[2];
            find_patterns(text)?;
        }
        
        "mem-stats" => {
            println!("Memory Stats: {:?}", memory_manager.get_memory_stats());
        }
        
        _ => {
            eprintln!("Unknown command: {}", command);
            eprintln!("Use one of: analyze, process, patch, patterns, mem-stats");
            process::exit(1);
        }
    }
    
    Ok(())
}

async fn perform_analysis(apk_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting analysis of: {}", apk_path);
    
    // Check if APK file exists
    if !Path::new(apk_path).exists() {
        return Err(format!("APK file does not exist: {}", apk_path).into());
    }
    
    // Create RustCracker instance
    let cracker = RustCracker::new(apk_path.to_string());
    
    // Perform analysis
    let result = cracker.analyze()?;
    
    // Output result as JSON
    let json_result = serde_json::to_string_pretty(&result)?;
    println!("{}", json_result);
    
    // Additional analysis information
    println!("\n=== Analysis Summary ===");
    println!("Vulnerabilities found: {}", result.vulnerabilities.len());
    println!("Protections detected: {}", result.protections.len());
    println!("Security Score: {}/100", result.security_score);
    
    Ok(())
}

async fn perform_processing(apk_path: &str, mode: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting processing of: {} with mode: {}", apk_path, mode);
    
    // Check if APK file exists
    if !Path::new(apk_path).exists() {
        return Err(format!("APK file does not exist: {}", apk_path).into());
    }
    
    // First, perform an analysis to get information about the APK
    let cracker = RustCracker::new(apk_path.to_string());
    let analysis = cracker.analyze()?;
    
    // Perform processing based on mode
    let patcher = BinaryPatcher::new(apk_path.to_string());
    let output_path = format!("{}_processed.apk", apk_path.trim_end_matches(".apk"));
    
    let success = match mode {
        "certificate_pinning_bypass" => patcher.patch_certificate_pinning(&output_path)?,
        "root_detection_bypass" => patcher.patch_root_detection(&output_path)?,
        "debug_bypass" => patcher.patch_debug_protection(&output_path)?,
        "iap_bypass" => patcher.patch_iap_verification(&output_path)?,
        "login_bypass" => patcher.patch_login_verification(&output_path)?,
        _ => {
            eprintln!("Unknown processing mode: {}", mode);
            return Ok(()); // Don't return error, just return
        }
    };
    
    if success {
        println!("Processing completed successfully!");
        println!("Output file: {}", output_path);
        
        // Create a result similar to what would be returned by the processing function
        let mut result = std::collections::HashMap::new();
        result.insert("success".to_string(), serde_json::Value::Bool(true));
        result.insert("modified_apk_path".to_string(), serde_json::Value::String(output_path));
        result.insert("fixes_applied".to_string(), serde_json::Value::Array(vec![
            serde_json::Value::String(format!("Applied {} patch", mode))
        ]));
        result.insert("stability_score".to_string(), serde_json::Value::Number(
            serde_json::Number::from(cracker.calculate_stability_score(&analysis))
        ));
        
        let json_result = serde_json::to_string_pretty(&result)?;
        println!("{}", json_result);
    } else {
        eprintln!("Processing failed!");
    }
    
    Ok(())
}

fn perform_patching(apk_path: &str, patch_type: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("Applying {} patch to: {}", patch_type, apk_path);
    
    // Check if APK file exists
    if !Path::new(apk_path).exists() {
        return Err(format!("APK file does not exist: {}", apk_path).into());
    }
    
    let patcher = BinaryPatcher::new(apk_path.to_string());
    let output_path = format!("{}_patched.apk", apk_path.trim_end_matches(".apk"));
    
    let success = patcher.patch_apk(patch_type, &output_path)?;
    
    if success {
        println!("Patch applied successfully!");
        println!("Output file: {}", output_path);
    } else {
        eprintln!("Patch application failed!");
    }
    
    Ok(())
}

fn find_patterns(text: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("Finding patterns in text: {}", text);
    
    // Create pattern matcher and load default patterns
    let mut matcher = PatternMatcher::new();
    matcher.load_default_patterns();
    
    // Find patterns
    let result = matcher.analyze_apk_for_patterns(text);
    
    // Output results
    println!("Found {} patterns:", result.found_patterns.len());
    for pattern in result.found_patterns {
        println!("  - {} ({}) at position {}: {}", 
            pattern.pattern_name, 
            pattern.severity, 
            pattern.position, 
            pattern.matched_text
        );
    }
    
    if !result.recommendations.is_empty() {
        println!("\nRecommendations:");
        for rec in result.recommendations {
            println!("  - {}: {}", rec.pattern_name, rec.description);
        }
    }
    
    // Show counts by severity
    println!("\nPattern counts:");
    println!("  Critical: {}", result.critical_count);
    println!("  High: {}", result.high_count);
    println!("  Medium: {}", result.medium_count);
    println!("  Low: {}", result.low_count);
    
    Ok(())
}

// Additional utility function
fn print_help() {
    println!("Rust Cracker - Binary manipulation tool");
    println!();
    println!("Commands:");
    println!("  analyze <apk_path>          - Analyze an APK for vulnerabilities");
    println!("  process <apk_path> <mode>   - Process/modify an APK");
    println!("  patch <apk_path> <type>     - Apply a specific patch to an APK");
    println!("  patterns <text>             - Find patterns in text");
    println!("  mem-stats                   - Show memory usage statistics");
    println!();
    println!("Processing modes:");
    println!("  certificate_pinning_bypass  - Bypass certificate pinning");
    println!("  root_detection_bypass       - Bypass root detection");
    println!("  debug_bypass               - Bypass anti-debug measures");
    println!("  iap_bypass                 - Bypass in-app purchase verification");
    println!("  login_bypass               - Bypass login authentication");
    println!();
    println!("Patch types:");
    println!("  certificate_pinning         - Remove certificate pinning");
    println!("  root_detection              - Remove root detection");
    println!("  debug_protection            - Remove debug protection");
    println!("  iap_verification            - Remove IAP verification");
    println!("  login_verification          - Remove login verification");
}