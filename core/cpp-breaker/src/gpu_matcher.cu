#include <cuda_runtime.h>
#include <iostream>
#include <vector>
#include <string>
#include <map>

// Define structures for GPU operations
struct GPUResult {
    int* matches;
    int count;
    int capacity;
};

// CUDA kernel for pattern matching
__global__ void pattern_match_kernel(const char* text, int text_len, 
                                     const char* pattern, int pattern_len, 
                                     int* results, int* result_count) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    for (int i = idx; i < text_len - pattern_len + 1; i += stride) {
        bool match = true;
        for (int j = 0; j < pattern_len; j++) {
            if (text[i + j] != pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) {
            int pos = atomicAdd(result_count, 1);
            if (pos < 10000) {  // Limit to prevent memory issues
                results[pos] = i;
            }
        }
    }
}

class GPUMatcher {
private:
    cudaStream_t stream;
    int* d_results;
    int* d_result_count;
    char* d_text;
    char* d_pattern;
    
public:
    GPUMatcher() {
        // Create CUDA stream
        cudaStreamCreate(&stream);
        
        // Allocate device memory for results (10k max matches)
        cudaMalloc(&d_results, 10000 * sizeof(int));
        cudaMalloc(&d_result_count, sizeof(int));
    }
    
    ~GPUMatcher() {
        if (d_results) cudaFree(d_results);
        if (d_result_count) cudaFree(d_result_count);
        if (d_text) cudaFree(d_text);
        if (d_pattern) cudaFree(d_pattern);
        cudaStreamDestroy(stream);
    }
    
    GPUResult match_pattern(const std::string& text, const std::string& pattern) {
        GPUResult result;
        result.capacity = 10000;
        result.matches = new int[result.capacity];
        result.count = 0;
        
        // Allocate device memory for text and pattern
        int text_len = text.length();
        int pattern_len = pattern.length();
        
        if (d_text) cudaFree(d_text);
        if (d_pattern) cudaFree(d_pattern);
        
        cudaMalloc(&d_text, text_len * sizeof(char));
        cudaMalloc(&d_pattern, pattern_len * sizeof(char));
        
        // Copy data to device
        cudaMemcpy(d_text, text.c_str(), text_len, cudaMemcpyHostToDevice);
        cudaMemcpy(d_pattern, pattern.c_str(), pattern_len, cudaMemcpyHostToDevice);
        
        // Initialize result count to 0
        int init_count = 0;
        cudaMemcpy(d_result_count, &init_count, sizeof(int), cudaMemcpyHostToDevice);
        
        // Configure kernel launch parameters
        int blockSize = 256;
        int numBlocks = (text_len + blockSize - 1) / blockSize;
        if (numBlocks > 65535) numBlocks = 65535; // Limit for older GPUs
        
        // Launch kernel
        pattern_match_kernel<<<numBlocks, blockSize, 0, stream>>>(
            d_text, text_len, d_pattern, pattern_len, d_results, d_result_count
        );
        
        // Wait for kernel to complete
        cudaStreamSynchronize(stream);
        
        // Copy results back to host
        cudaMemcpy(&result.count, d_result_count, sizeof(int), cudaMemcpyDeviceToHost);
        if (result.count > 0) {
            int h_results[10000];
            cudaMemcpy(h_results, d_results, result.count * sizeof(int), cudaMemcpyDeviceToHost);
            
            // Copy to result array
            for (int i = 0; i < result.count; i++) {
                result.matches[i] = h_results[i];
            }
        }
        
        return result;
    }
    
    // Alternative method for matching multiple patterns at once
    std::map<std::string, GPUResult> match_multiple_patterns(const std::string& text, 
                                                            const std::vector<std::string>& patterns) {
        std::map<std::string, GPUResult> all_results;
        
        for (const auto& pattern : patterns) {
            all_results[pattern] = match_pattern(text, pattern);
        }
        
        return all_results;
    }
    
    // Method to check if GPU is available
    static bool is_gpu_available() {
        int deviceCount = 0;
        cudaError_t error = cudaGetDeviceCount(&deviceCount);
        
        return (error == cudaSuccess && deviceCount > 0);
    }
    
    // Method to get GPU information
    static std::map<std::string, std::string> get_gpu_info() {
        std::map<std::string, std::string> info;
        
        int deviceCount;
        cudaGetDeviceCount(&deviceCount);
        
        info["device_count"] = std::to_string(deviceCount);
        
        if (deviceCount > 0) {
            cudaDeviceProp prop;
            cudaGetDeviceProperties(&prop, 0);
            
            info["device_name"] = std::string(prop.name);
            info["compute_capability"] = std::to_string(prop.major) + "." + std::to_string(prop.minor);
            info["total_memory_mb"] = std::to_string(prop.totalGlobalMem / (1024 * 1024));
            info["clock_rate_khz"] = std::to_string(prop.clockRate);
            info["multiprocessor_count"] = std::to_string(prop.multiProcessorCount);
        }
        
        return info;
    }
};

// Example usage
int main() {
    if (!GPUMatcher::is_gpu_available()) {
        std::cout << "No CUDA-capable GPU found!" << std::endl;
        return 1;
    }
    
    std::cout << "GPU is available!" << std::endl;
    
    // Get GPU info
    auto gpu_info = GPUMatcher::get_gpu_info();
    std::cout << "GPU Info:" << std::endl;
    for (const auto& pair : gpu_info) {
        std::cout << "  " << pair.first << ": " << pair.second << std::endl;
    }
    
    // Example pattern matching
    GPUMatcher matcher;
    std::string text = "This is a test string for pattern matching. Testing patterns in this text.";
    std::string pattern = "test";
    
    GPUResult result = matcher.match_pattern(text, pattern);
    
    std::cout << "\nPattern '" << pattern << "' found " << result.count << " times:" << std::endl;
    for (int i = 0; i < result.count; i++) {
        std::cout << "  Position: " << result.matches[i] << std::endl;
    }
    
    // Clean up
    delete[] result.matches;
    
    return 0;
}