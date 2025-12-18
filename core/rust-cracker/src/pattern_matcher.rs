use std::collections::HashMap;
use regex::Regex;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CrackPattern {
    pub name: String,
    pub description: String,
    pub pattern_type: String, // e.g., "regex", "byte_sequence", "smali_pattern"
    pub pattern: String,
    pub severity: String,     // CRITICAL, HIGH, MEDIUM, LOW
    pub applicable_to: Vec<String>, // Categories this pattern applies to
    pub patch_template: String, // Name of patch template to apply
}

pub struct PatternMatcher {
    pub crack_patterns: Vec<CrackPattern>,
    pub compiled_patterns: HashMap<String, Regex>,
}

impl PatternMatcher {
    pub fn new() -> Self {
        Self {
            crack_patterns: Vec::new(),
            compiled_patterns: HashMap::new(),
        }
    }

    pub fn load_default_patterns(&mut self) {
        // Define common crack patterns
        let default_patterns = vec![
            CrackPattern {
                name: "Certificate Pinning".to_string(),
                description: "Certificate pinning implementation".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "checkServerTrusted|X509TrustManager|SSLSocketFactory".to_string(),
                severity: "MEDIUM".to_string(),
                applicable_to: vec!["network".to_string(), "security".to_string()],
                patch_template: "cert_pinning_bypass".to_string(),
            },
            CrackPattern {
                name: "Root Detection".to_string(),
                description: "Root detection implementation".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "isRooted|rootbeer|root check|superuser".to_string(),
                severity: "MEDIUM".to_string(),
                applicable_to: vec!["security".to_string(), "utility".to_string()],
                patch_template: "root_detection_bypass".to_string(),
            },
            CrackPattern {
                name: "Anti-Debug".to_string(),
                description: "Anti-debugging implementation".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "isDebuggerConnected|debugger|jdwp".to_string(),
                severity: "MEDIUM".to_string(),
                applicable_to: vec!["security".to_string(), "banking".to_string()],
                patch_template: "anti_debug_bypass".to_string(),
            },
            CrackPattern {
                name: "Hardcoded API Key".to_string(),
                description: "Hardcoded API key in code".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "api[_-]?key|token|secret".to_string(),
                severity: "CRITICAL".to_string(),
                applicable_to: vec!["all".to_string()],
                patch_template: "remove_hardcoded_creds".to_string(),
            },
            CrackPattern {
                name: "In-App Purchase".to_string(),
                description: "In-app purchase verification logic".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "billing|purchase|receipt|verify".to_string(),
                severity: "HIGH".to_string(),
                applicable_to: vec!["game".to_string(), "utility".to_string(), "media".to_string()],
                patch_template: "iap_bypass".to_string(),
            },
            CrackPattern {
                name: "Login Authentication".to_string(),
                description: "Login/authentication verification".to_string(),
                pattern_type: "regex".to_string(),
                pattern: "login|authenticate|auth|session".to_string(),
                severity: "HIGH".to_string(),
                applicable_to: vec!["social".to_string(), "finance".to_string(), "utility".to_string()],
                patch_template: "auth_bypass".to_string(),
            },
        ];

        for pattern in default_patterns {
            self.add_pattern(pattern);
        }
    }

    pub fn add_pattern(&mut self, pattern: CrackPattern) {
        if pattern.pattern_type == "regex" {
            if let Ok(compiled_regex) = Regex::new(&pattern.pattern) {
                self.compiled_patterns.insert(pattern.name.clone(), compiled_regex);
            }
        }
        self.crack_patterns.push(pattern);
    }

    pub fn find_patterns_in_text(&self, text: &str) -> Vec<FoundPattern> {
        let mut found_patterns = Vec::new();

        for pattern in &self.crack_patterns {
            if let Some(compiled_regex) = self.compiled_patterns.get(&pattern.name) {
                for mat in compiled_regex.find_iter(text) {
                    found_patterns.push(FoundPattern {
                        pattern_name: pattern.name.clone(),
                        pattern_type: pattern.pattern_type.clone(),
                        matched_text: mat.as_str().to_string(),
                        position: mat.start(),
                        severity: pattern.severity.clone(),
                        description: pattern.description.clone(),
                        patch_template: pattern.patch_template.clone(),
                    });
                }
            }
        }

        found_patterns
    }

    pub fn find_patterns_by_category(&self, text: &str, category: &str) -> Vec<FoundPattern> {
        let mut found_patterns = Vec::new();

        for pattern in &self.crack_patterns {
            // Check if this pattern applies to the specified category
            if pattern.applicable_to.contains(&"all".to_string()) || 
               pattern.applicable_to.contains(&category.to_string()) {
                
                if let Some(compiled_regex) = self.compiled_patterns.get(&pattern.name) {
                    for mat in compiled_regex.find_iter(text) {
                        found_patterns.push(FoundPattern {
                            pattern_name: pattern.name.clone(),
                            pattern_type: pattern.pattern_type.clone(),
                            matched_text: mat.as_str().to_string(),
                            position: mat.start(),
                            severity: pattern.severity.clone(),
                            description: pattern.description.clone(),
                            patch_template: pattern.patch_template.clone(),
                        });
                    }
                }
            }
        }

        found_patterns
    }

    pub fn get_crack_recommendations(&self, found_patterns: &[FoundPattern]) -> Vec<CrackRecommendation> {
        let mut recommendations = Vec::new();

        for found_pattern in found_patterns {
            let recommendation = CrackRecommendation {
                pattern_name: found_pattern.pattern_name.clone(),
                severity: found_pattern.severity.clone(),
                patch_template: found_pattern.patch_template.clone(),
                description: format!("Found {} pattern that can be bypassed", found_pattern.pattern_name),
            };
            recommendations.push(recommendation);
        }

        recommendations
    }

    pub fn get_pattern_by_name(&self, name: &str) -> Option<&CrackPattern> {
        self.crack_patterns.iter().find(|p| p.name == name)
    }
}

#[derive(Debug, Clone)]
pub struct FoundPattern {
    pub pattern_name: String,
    pub pattern_type: String,
    pub matched_text: String,
    pub position: usize,
    pub severity: String,
    pub description: String,
    pub patch_template: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CrackRecommendation {
    pub pattern_name: String,
    pub severity: String,
    pub patch_template: String,
    pub description: String,
}

impl PatternMatcher {
    pub fn analyze_apk_for_patterns(&self, apk_content: &str) -> PatternAnalysisResult {
        let mut result = PatternAnalysisResult {
            found_patterns: Vec::new(),
            recommendations: Vec::new(),
            critical_count: 0,
            high_count: 0,
            medium_count: 0,
            low_count: 0,
        };

        // Find all patterns
        result.found_patterns = self.find_patterns_in_text(apk_content);

        // Generate recommendations
        result.recommendations = self.get_crack_recommendations(&result.found_patterns);

        // Count by severity
        for pattern in &result.found_patterns {
            match pattern.severity.as_str() {
                "CRITICAL" => result.critical_count += 1,
                "HIGH" => result.high_count += 1,
                "MEDIUM" => result.medium_count += 1,
                "LOW" => result.low_count += 1,
                _ => {} // Unknown severity
            }
        }

        result
    }

    pub fn suggest_crack_method(&self, app_category: &str, apk_content: &str) -> Vec<String> {
        let mut suggestions = Vec::new();

        let patterns = self.find_patterns_by_category(apk_content, app_category);
        
        for pattern in patterns {
            match pattern.pattern_name.as_str() {
                "Certificate Pinning" => {
                    suggestions.push("Bypass certificate pinning to intercept traffic".to_string());
                },
                "Root Detection" => {
                    suggestions.push("Bypass root detection to access protected features".to_string());
                },
                "Anti-Debug" => {
                    suggestions.push("Disable anti-debug mechanisms for dynamic analysis".to_string());
                },
                "In-App Purchase" => {
                    suggestions.push("Bypass in-app purchase verification for premium features".to_string());
                },
                "Login Authentication" => {
                    suggestions.push("Bypass login authentication to access premium content".to_string());
                },
                _ => {
                    suggestions.push(format!("Potential bypass for: {}", pattern.pattern_name));
                }
            }
        }

        suggestions
    }
}

#[derive(Debug)]
pub struct PatternAnalysisResult {
    pub found_patterns: Vec<FoundPattern>,
    pub recommendations: Vec<CrackRecommendation>,
    pub critical_count: usize,
    pub high_count: usize,
    pub medium_count: usize,
    pub low_count: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pattern_matcher_creation() {
        let matcher = PatternMatcher::new();
        assert_eq!(matcher.crack_patterns.len(), 0);
    }

    #[test]
    fn test_load_default_patterns() {
        let mut matcher = PatternMatcher::new();
        matcher.load_default_patterns();
        
        assert!(matcher.crack_patterns.len() > 0);
        assert!(matcher.compiled_patterns.len() > 0);
    }

    #[test]
    fn test_find_patterns() {
        let mut matcher = PatternMatcher::new();
        matcher.load_default_patterns();
        
        let test_text = "This app has rootbeer check and uses X509TrustManager";
        let found = matcher.find_patterns_in_text(test_text);
        
        assert!(!found.is_empty());
        // Should find both root detection and certificate pinning patterns
        assert!(found.iter().any(|p| p.pattern_name == "Root Detection"));
        assert!(found.iter().any(|p| p.pattern_name == "Certificate Pinning"));
    }

    #[test]
    fn test_pattern_analysis() {
        let mut matcher = PatternMatcher::new();
        matcher.load_default_patterns();
        
        let test_text = "This app checks for debugger and has hardcoded API keys";
        let result = matcher.analyze_apk_for_patterns(test_text);
        
        assert!(result.found_patterns.len() >= 1);
        assert!(!result.recommendations.is_empty());
    }
}