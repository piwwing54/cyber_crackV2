FROM ubuntu:20.04

# Install build dependencies (without CUDA-specific requirements initially)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    git \
    curl \
    ca-certificates \
    wget \
    python3 \
    python3-pip \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source files
COPY . .

# Create build directory
RUN mkdir build

WORKDIR /build

# Configure with CMake (will use CPU-only build if no CUDA)
RUN cmake .. -DCMAKE_BUILD_TYPE=Release -DUSE_CUDA=OFF

# Build the project
RUN make -j$(nproc)

# Expose port
EXPOSE 8082

# Run the application
CMD ["./cpp-breaker"]