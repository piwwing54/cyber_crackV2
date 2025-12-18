FROM rust:1.75

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy cargo files first for better caching
COPY Cargo.toml Cargo.lock ./

# Create a dummy main.rs so we can build dependencies
RUN mkdir src
RUN echo "fn main() { println!(\"Dummy build\"); }" > src/main.rs

# Build dependencies
RUN cargo build --release
RUN rm -rf src

# Copy actual source
COPY src/ ./src/

# Build the actual project
RUN cargo build --release

# Expose port
EXPOSE 8081

# Run the application
CMD ["./target/release/rust-cracker"]