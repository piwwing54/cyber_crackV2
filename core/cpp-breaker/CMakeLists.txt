cmake_minimum_required(VERSION 3.18)
project(cpp-breaker)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find CUDA
find_package(CUDA REQUIRED)

# Set CUDA architectures (adjust based on your target GPUs)
set(CMAKE_CUDA_ARCHITECTURES 61 75 86)

# Add executable
add_executable(main
    src/main.cpp
    src/pattern_engine.cpp
    src/simd_scanner.cpp
    src/apk_processor.cpp
)

# Add CUDA executable for GPU matcher
add_executable(gpu_matcher
    src/gpu_matcher.cu
)

# Link necessary libraries
target_link_libraries(main)

# Set CUDA properties for the GPU matcher
set_property(TARGET gpu_matcher PROPERTY CUDA_SEPARABLE_COMPILATION ON)

# Installation rules
install(TARGETS main gpu_matcher
    RUNTIME DESTINATION bin
)