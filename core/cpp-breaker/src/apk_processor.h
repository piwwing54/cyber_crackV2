#ifndef APK_PROCESSOR_H
#define APK_PROCESSOR_H

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

// Structure for a patch to apply to an APK
struct Patch {
    size_t offset;
    std::string original_bytes;
    std::string patched_bytes;
    std::string description;
};

class ApkProcessor {
public:
    ApkProcessor();
    ~ApkProcessor() = default;
    
    // Get protections present in the APK
    std::vector<std::string> get_protections(const std::string& apk_path);
    
    // Bypass root detection in the APK
    bool bypass_root_detection(const std::string& apk_path);
    
    // Bypass certificate pinning in the APK
    bool bypass_certificate_pinning(const std::string& apk_path);
    
    // Disable debug detection in the APK
    bool disable_debug_detection(const std::string& apk_path);
    
    // Apply a set of patches to the APK
    bool apply_patches(const std::string& apk_path, const std::vector<Patch>& patches);
    
    // Decompile an APK
    bool decompile_apk(const std::string& apk_path, const std::string& output_dir);
    
    // Rebuild an APK from decompiled source
    bool rebuild_apk(const std::string& input_dir, const std::string& output_path);
    
    // Sign an APK
    bool sign_apk(const std::string& apk_path, const std::string& keystore_path);
    
    // Verify APK signature
    bool verify_signature(const std::string& apk_path);
    
private:
    // Helper method to find files in a directory
    std::vector<std::string> find_files(const std::string& directory, 
                                       const std::string& extension);
    
    // Helper method to read file contents
    std::string read_file_contents(const std::string& file_path);
    
    // Helper method to write file contents
    bool write_file_contents(const std::string& file_path, const std::string& content);
    
    // Internal implementation methods for bypasses
    bool internal_bypass_root_detection(const std::string& decompiled_dir);
    bool internal_bypass_cert_pinning(const std::string& decompiled_dir);
    bool internal_disable_debug_detection(const std::string& decompiled_dir);
};

#endif // APK_PROCESSOR_H