#ifndef PATTERN_ENGINE_H
#define PATTERN_ENGINE_H

#include <vector>
#include <string>
#include <map>
#include <regex>
#include <memory>
#include <thread>
#include <mutex>
#include <future>
#include <unordered_map>

struct PatternMatch {
    std::string pattern_id;
    std::string matched_text;
    std::string file_path;
    int line_number;
    double confidence;
    std::string context;
    std::string fix_suggestion;
};

struct CrackPattern {
    std::string id;
    std::string name;
    std::string pattern_type;  // regex, string, binary, etc.
    std::string pattern;
    std::string category;      // login_bypass, iap_crack, etc.
    std::string subcategory;
    std::string severity;      // CRITICAL, HIGH, MEDIUM, LOW
    double confidence;
    std::string description;
    std::string fix_suggestion;
    bool enabled;
    std::regex compiled_regex; // For regex patterns
    
    CrackPattern(const std::string& id, 
                 const std::string& name,
                 const std::string& type,
                 const std::string& pat,
                 const std::string& cat,
                 const std::string& subcat,
                 const std::string& sev,
                 double conf,
                 const std::string& desc,
                 const std::string& fix_sug,
                 bool en = true)
        : id(id), name(name), pattern_type(type), pattern(pat), category(cat), 
          subcategory(subcat), severity(sev), confidence(conf), 
          description(desc), fix_suggestion(fix_sug), enabled(en) {
        
        if (pattern_type == "regex") {
            compiled_regex = std::regex(pattern, std::regex_constants::icase);
        }
    }
};

class PatternEngine {
private:
    std::vector<CrackPattern> patterns_;
    std::unordered_map<std::string, std::vector<CrackPattern>> category_patterns_;
    std::map<std::string, int> pattern_stats_;
    mutable std::mutex stats_mutex_;
    
    int num_threads_;
    bool simd_enabled_;
    bool gpu_acceleration_;

public:
    PatternEngine(int num_threads = std::thread::hardware_concurrency());
    ~PatternEngine() = default;
    
    void set_num_threads(int num_threads) { num_threads_ = num_threads; }
    void enable_simd(bool enable) { simd_enabled_ = enable; }
    void enable_gpu_acceleration(bool enable) { gpu_acceleration_ = enable; }
    
    // Add pattern methods
    void add_pattern(const CrackPattern& pattern);
    void add_patterns(const std::vector<CrackPattern>& patterns);
    void remove_pattern(const std::string& pattern_id);
    
    // Pattern matching methods
    std::vector<PatternMatch> find_patterns_in_file(const std::string& file_path);
    std::vector<PatternMatch> find_patterns_in_content(const std::string& content, 
                                                       const std::string& file_path);
    std::vector<PatternMatch> find_patterns_in_directory(const std::string& dir_path);
    std::vector<PatternMatch> find_patterns_in_apk(const std::string& apk_path);
    
    // Category-specific methods
    std::vector<PatternMatch> find_login_bypass_patterns(const std::string& content, 
                                                         const std::string& file_path);
    std::vector<PatternMatch> find_iap_patterns(const std::string& content, 
                                                const std::string& file_path);
    std::vector<PatternMatch> find_root_detection_patterns(const std::string& content, 
                                                           const std::string& file_path);
    std::vector<PatternMatch> find_certificate_pinning_patterns(const std::string& content, 
                                                                const std::string& file_path);
    std::vector<PatternMatch> find_debug_detection_patterns(const std::string& content, 
                                                            const std::string& file_path);
    
    // Advanced pattern matching using SIMD instructions
    std::vector<PatternMatch> find_patterns_simd(const std::string& content, 
                                                 const std::string& file_path);
    
    // GPU-accelerated pattern matching
    std::vector<PatternMatch> find_patterns_gpu(const std::string& content, 
                                                const std::string& file_path);
    
    // Bulk operations
    std::vector<std::vector<PatternMatch>> find_patterns_bulk(
        const std::vector<std::pair<std::string, std::string>>& file_contents);
    
    // Pattern management
    std::vector<CrackPattern> get_patterns_by_category(const std::string& category);
    std::vector<CrackPattern> get_all_patterns() const { return patterns_; }
    size_t get_pattern_count() const { return patterns_.size(); }
    
    // Statistics and reporting
    std::map<std::string, int> get_pattern_stats() const;
    void reset_stats();
    
    // Load/save patterns from/to files
    bool load_patterns_from_json(const std::string& file_path);
    bool save_patterns_to_json(const std::string& file_path) const;
    
    // Pattern compilation and optimization
    void compile_patterns();
    void optimize_patterns();
    
    // Update pattern confidence based on real-world results
    void update_pattern_confidence(const std::string& pattern_id, double new_confidence);
    
private:
    // Internal matching methods
    std::vector<PatternMatch> find_patterns_internal(const std::string& content, 
                                                     const std::string& file_path,
                                                     const std::vector<CrackPattern>& patterns);
    
    // SIMD-accelerated matching (requires CPU with SIMD support)
    std::vector<PatternMatch> find_patterns_simd_internal(const std::string& content, 
                                                          const std::string& file_path);
    
    // Helper methods for file operations
    std::string read_file_content(const std::string& file_path);
    std::vector<std::string> get_files_with_extension(const std::string& dir_path, 
                                                      const std::string& ext);
    
    // Extract context around matches
    std::string extract_context(const std::string& content, 
                                size_t match_pos, 
                                size_t match_len, 
                                size_t context_size = 50);
};

// Implementation of inline methods
inline std::string PatternEngine::extract_context(const std::string& content, 
                                                  size_t match_pos, 
                                                  size_t match_len, 
                                                  size_t context_size) {
    size_t start = (match_pos < context_size) ? 0 : match_pos - context_size;
    size_t end = std::min(content.length(), match_pos + match_len + context_size);
    
    std::string context = content.substr(start, end - start);
    
    // Add ellipsis if we cropped the beginning or end
    if (start > 0) {
        context = "..." + context;
    }
    if (end < content.length()) {
        context = context + "...";
    }
    
    return context;
}

#endif // PATTERN_ENGINE_H