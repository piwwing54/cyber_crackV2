FROM golang:1.21-alpine AS builder

# Install git and other dependencies
RUN apk add --no-cache git gcc musl-dev linux-headers

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=1 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o main .

# Final stage
FROM alpine:3.18

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/main .

# Copy any additional tools
COPY tools/ /tools/

# Expose port
EXPOSE 8080

# Run the application
CMD ["./main"]