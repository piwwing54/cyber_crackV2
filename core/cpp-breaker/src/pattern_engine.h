#ifndef PATTERN_ENGINE_H
#define PATTERN_ENGINE_H

#include <string>
#include <vector>
#include <regex>
#include <nlohmann/json.hpp>

// Structure for a pattern to match
struct Pattern {
    std::string id;
    std::string description;
    std::string pattern_type;
    std::regex regex_pattern;
    std::string severity;
    std::string fix_suggestion;
};

// Structure for a match result
struct MatchResult {
    std::string pattern_id;
    std::string pattern_type;
    std::string description;
    std::string severity;
    std::string file_path;
    std::string matched_text;
    std::string context;
    int line_number;
    std::string fix_suggestion;
};

class PatternEngine {
public:
    PatternEngine();
    ~PatternEngine() = default;
    
    // Scan an APK for patterns
    std::vector<nlohmann::json> scan_apk(const std::string& apk_path);
    
    // Scan a specific file for patterns
    std::vector<MatchResult> scan_file(const std::string& file_path);
    
    // Add a new pattern to the engine
    void add_pattern(const Pattern& pattern);
    
    // Remove a pattern by ID
    void remove_pattern(const std::string& pattern_id);
    
    // Get the number of loaded patterns
    size_t get_pattern_count() const { return patterns_.size(); }

private:
    std::vector<Pattern> patterns_;
    
    // Load default patterns
    void load_default_patterns();
    
    // Helper function to read file contents
    std::string read_file_contents(const std::string& file_path);
};

#endif // PATTERN_ENGINE_H