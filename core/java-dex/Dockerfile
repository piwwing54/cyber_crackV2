FROM maven:3.9.5-eclipse-temurin-17 AS build

WORKDIR /app

# Copy pom.xml first to leverage Docker layer caching
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline -q

# Copy source code
COPY src/ ./src/

# Build the application
RUN mvn clean package -q -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Install Android SDK tools if needed
RUN apk add --no-cache wget unzip && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O sdk-tools.zip && \
    unzip sdk-tools.zip && \
    mkdir -p /opt/android-sdk/cmdline-tools && \
    mv cmdline-tools /opt/android-sdk/cmdline-tools/latest && \
    rm sdk-tools.zip && \
    apk del wget unzip

# Set environment variables
ENV ANDROID_HOME=/opt/android-sdk

# Copy the JAR file from build stage
COPY --from=build /app/target/*.jar app.jar

# Expose port
EXPOSE 8083

# Run the application
CMD ["java", "-jar", "app.jar"]