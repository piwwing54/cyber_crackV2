#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <filesystem>
#include <memory>

// Structure to store pattern match results
struct PatternMatch {
    std::string pattern_name;
    std::string matched_text;
    int position;
    std::string severity;
    std::string description;
    std::string patch_template;
};

// Structure for pattern definition
struct PatternDefinition {
    std::string name;
    std::string description;
    std::string pattern_type;  // regex, string, etc.
    std::string pattern;
    std::string severity;      // CRITICAL, HIGH, MEDIUM, LOW
    std::vector<std::string> applicable_to;  // Categories this applies to
    std::string patch_template;
    
    // Compiled regex for faster matching (when pattern_type is "regex")
    std::unique_ptr<std::regex> compiled_regex;
    
    PatternDefinition(const std::string& n, const std::string& d, const std::string& pt,
                     const std::string& p, const std::string& s, 
                     const std::vector<std::string>& app_to, const std::string& patch_t)
        : name(n), description(d), pattern_type(pt), pattern(p), severity(s), 
          applicable_to(app_to), patch_template(patch_t) {
        
        if (pt == "regex") {
            try {
                compiled_regex = std::make_unique<std::regex>(p, std::regex_constants::icase);
            } catch (const std::regex_error& e) {
                std::cerr << "Regex compilation error for pattern " << n << ": " << e.what() << std::endl;
            }
        }
    }
};

class PatternEngine {
private:
    std::vector<PatternDefinition> patterns;
    
public:
    PatternEngine() {
        load_default_patterns();
    }
    
    void load_default_patterns() {
        // Define common crack patterns
        std::vector<std::string> all_categories = {"all"};
        std::vector<std::string> security_categories = {"security"};
        std::vector<std::string> app_categories = {"game", "utility", "media", "social", "finance"};
        
        add_pattern(PatternDefinition(
            "Certificate Pinning", 
            "Certificate pinning implementation",
            "regex",
            "checkServerTrusted|X509TrustManager|SSLSocketFactory",
            "MEDIUM",
            security_categories,
            "cert_pinning_bypass"
        ));
        
        add_pattern(PatternDefinition(
            "Root Detection", 
            "Root detection implementation",
            "regex",
            "isRooted|rootbeer|root check|superuser",
            "MEDIUM",
            security_categories,
            "root_detection_bypass"
        ));
        
        add_pattern(PatternDefinition(
            "Anti-Debug", 
            "Anti-debugging implementation",
            "regex",
            "isDebuggerConnected|debugger|jdwp",
            "MEDIUM",
            app_categories,
            "anti_debug_bypass"
        ));
        
        add_pattern(PatternDefinition(
            "Hardcoded API Key", 
            "Hardcoded API key in code",
            "regex",
            "api[_-]?key|token|secret",
            "CRITICAL",
            all_categories,
            "remove_hardcoded_creds"
        ));
        
        add_pattern(PatternDefinition(
            "In-App Purchase", 
            "In-app purchase verification logic",
            "regex",
            "billing|purchase|receipt|verify",
            "HIGH",
            app_categories,
            "iap_bypass"
        ));
        
        add_pattern(PatternDefinition(
            "Login Authentication", 
            "Login/authentication verification",
            "regex",
            "login|authenticate|auth|session",
            "HIGH",
            app_categories,
            "auth_bypass"
        ));
        
        add_pattern(PatternDefinition(
            "Weak Cryptography", 
            "Use of weak cryptographic algorithms",
            "regex",
            "MD5|DES|RC4|Base64",
            "HIGH",
            security_categories,
            "crypto_upgrade"
        ));
        
        add_pattern(PatternDefinition(
            "SQL Injection Point", 
            "Potential SQL injection vulnerability",
            "regex",
            "execSQL|rawQuery|SELECT [^']*\'[^']*\'",
            "HIGH",
            all_categories,
            "sql_injection_fix"
        ));
    }
    
    void add_pattern(const PatternDefinition& pattern) {
        patterns.push_back(pattern);
    }
    
    std::vector<PatternMatch> find_patterns_in_text(const std::string& text) {
        std::vector<PatternMatch> found_patterns;
        
        for (const auto& pattern : patterns) {
            if (pattern.compiled_regex) {
                // Use regex to find all matches
                auto begin = std::sregex_iterator(text.begin(), text.end(), *pattern.compiled_regex);
                auto end = std::sregex_iterator();
                
                for (std::sregex_iterator i = begin; i != end; ++i) {
                    std::smatch match = *i;
                    PatternMatch found_match;
                    found_match.pattern_name = pattern.name;
                    found_match.matched_text = match.str();
                    found_match.position = match.position();
                    found_match.severity = pattern.severity;
                    found_match.description = pattern.description;
                    found_match.patch_template = pattern.patch_template;
                    
                    found_patterns.push_back(found_match);
                }
            }
        }
        
        return found_patterns;
    }
    
    std::vector<PatternMatch> find_patterns_by_category(const std::string& text, const std::string& category) {
        std::vector<PatternMatch> found_patterns;
        
        for (const auto& pattern : patterns) {
            // Check if this pattern applies to the specified category
            if (std::find(pattern.applicable_to.begin(), pattern.applicable_to.end(), "all") != pattern.applicable_to.end() ||
                std::find(pattern.applicable_to.begin(), pattern.applicable_to.end(), category) != pattern.applicable_to.end()) {
                
                if (pattern.compiled_regex) {
                    auto begin = std::sregex_iterator(text.begin(), text.end(), *pattern.compiled_regex);
                    auto end = std::sregex_iterator();
                    
                    for (std::sregex_iterator i = begin; i != end; ++i) {
                        std::smatch match = *i;
                        PatternMatch found_match;
                        found_match.pattern_name = pattern.name;
                        found_match.matched_text = match.str();
                        found_match.position = match.position();
                        found_match.severity = pattern.severity;
                        found_match.description = pattern.description;
                        found_match.patch_template = pattern.patch_template;
                        
                        found_patterns.push_back(found_match);
                    }
                }
            }
        }
        
        return found_patterns;
    }
    
    // Method to analyze a file for patterns
    std::vector<PatternMatch> analyze_file(const std::string& file_path) {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            std::cerr << "Could not open file: " << file_path << std::endl;
            return {};
        }
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string content = buffer.str();
        
        return find_patterns_in_text(content);
    }
    
    // Method to analyze an entire directory
    std::map<std::string, std::vector<PatternMatch>> analyze_directory(const std::string& dir_path) {
        std::map<std::string, std::vector<PatternMatch>> results;
        
        for (const auto& entry : std::filesystem::recursive_directory_iterator(dir_path)) {
            if (entry.is_regular_file()) {
                std::string path = entry.path().string();
                // Only analyze text-based files
                if (is_text_file(path)) {
                    auto file_results = analyze_file(path);
                    if (!file_results.empty()) {
                        results[path] = file_results;
                    }
                }
            }
        }
        
        return results;
    }
    
private:
    bool is_text_file(const std::string& file_path) {
        std::vector<std::string> text_extensions = {
            ".txt", ".java", ".smali", ".xml", ".json", ".js", ".html", ".css", 
            ".py", ".cpp", ".c", ".h", ".go", ".rs", ".swift", ".kt", ".scala"
        };
        
        std::string ext = std::filesystem::path(file_path).extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        
        return std::find(text_extensions.begin(), text_extensions.end(), ext) != text_extensions.end();
    }
};

// Structure for analysis result
struct PatternAnalysisResult {
    std::vector<PatternMatch> found_patterns;
    int critical_count;
    int high_count;
    int medium_count;
    int low_count;
    
    PatternAnalysisResult() : critical_count(0), high_count(0), medium_count(0), low_count(0) {}
};

class PatternAnalyzer {
private:
    PatternEngine engine;
    
public:
    PatternAnalysisResult analyze_text(const std::string& text) {
        PatternAnalysisResult result;
        result.found_patterns = engine.find_patterns_in_text(text);
        
        // Count by severity
        for (const auto& pattern : result.found_patterns) {
            if (pattern.severity == "CRITICAL") result.critical_count++;
            else if (pattern.severity == "HIGH") result.high_count++;
            else if (pattern.severity == "MEDIUM") result.medium_count++;
            else if (pattern.severity == "LOW") result.low_count++;
        }
        
        return result;
    }
    
    // Method to suggest crack methods based on app category
    std::vector<std::string> suggest_crack_methods(const std::string& category, const std::string& content) {
        std::vector<std::string> suggestions;
        auto patterns = engine.find_patterns_by_category(content, category);
        
        for (const auto& pattern : patterns) {
            if (pattern.pattern_name == "Certificate Pinning") {
                suggestions.push_back("Bypass certificate pinning to intercept traffic");
            } else if (pattern.pattern_name == "Root Detection") {
                suggestions.push_back("Bypass root detection to access protected features");
            } else if (pattern.pattern_name == "Anti-Debug") {
                suggestions.push_back("Disable anti-debug mechanisms for dynamic analysis");
            } else if (pattern.pattern_name == "In-App Purchase") {
                suggestions.push_back("Bypass in-app purchase verification for premium features");
            } else if (pattern.pattern_name == "Login Authentication") {
                suggestions.push_back("Bypass login authentication to access premium content");
            } else {
                suggestions.push_back("Potential bypass for: " + pattern.pattern_name);
            }
        }
        
        return suggestions;
    }
    
    // Get the pattern engine for direct access
    PatternEngine& get_engine() { return engine; }
};

#ifdef PATTERN_ENGINE_TEST
int main() {
    PatternEngine engine;
    std::string test_text = "This app checks for rootbeer and uses X509TrustManager for security.";
    
    auto matches = engine.find_patterns_in_text(test_text);
    
    std::cout << "Found " << matches.size() << " patterns:" << std::endl;
    for (const auto& match : matches) {
        std::cout << "  " << match.pattern_name << " ('" << match.matched_text 
                  << "') at position " << match.position << std::endl;
    }
    
    return 0;
}
#endif