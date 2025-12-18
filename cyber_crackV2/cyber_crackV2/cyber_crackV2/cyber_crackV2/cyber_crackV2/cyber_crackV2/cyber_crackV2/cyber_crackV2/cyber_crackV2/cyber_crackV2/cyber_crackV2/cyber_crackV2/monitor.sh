#!/bin/bash
# CYBER CRACK PRO - Monitoring Script
# Real-time monitoring for system health and performance

set -e  # Exit on any error

# Configuration
LOG_FILE="/var/log/cyber-crack-pro/monitor.log"
ALERT_EMAIL=""  # Set this to receive email alerts
ALERT_WEBHOOK=""  # Set this to send alerts to a webhook

# Function to check if a command exists
command_exists() {
    command -v "$@" > /dev/null 2>&1
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local message="$1"
    log_message "ALERT: $message"
    
    # Send email alert if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "CyberCrackPro Alert" "$ALERT_EMAIL"
    fi
    
    # Send webhook alert if configured
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\"}" "$ALERT_WEBHOOK"
    fi
}

# Check system resources
check_system_resources() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local memory_usage=$(free | grep Mem | awk '{printf("%.2f", ($3/$2) * 100.0)}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    log_message "System Resources - CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: ${disk_usage}%"
    
    # Check if resources are exceeding thresholds
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        send_alert "HIGH CPU USAGE: ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        send_alert "HIGH MEMORY USAGE: ${memory_usage}%"
    fi
    
    if [ "$disk_usage" -gt 80 ]; then
        send_alert "HIGH DISK USAGE: ${disk_usage}%"
    fi
}

# Check Docker container status
check_containers() {
    if command_exists docker; then
        local containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
        
        log_message "Container Status:"
        log_message "$containers"
        
        # Check for stopped containers
        local stopped=$(docker ps -a --filter "status=exited" --format "{{.Names}}" 2>/dev/null)
        if [ -n "$stopped" ]; then
            send_alert "STOPPED CONTAINERS FOUND: $stopped"
        fi
    fi
}

# Check service health
check_service_health() {
    # Check if main API is responding
    if curl -f -s http://localhost:5000/health >/dev/null 2>&1; then
        log_message "Main API: HEALTHY"
    else
        send_alert "MAIN API UNRESPONSIVE"
    fi
    
    # Check if other services are responding
    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
        log_message "Go Analyzer: HEALTHY"
    else
        log_message "Go Analyzer: UNRESPONSIVE"
    fi
    
    if curl -f -s http://localhost:8081/health >/dev/null 2>&1; then
        log_message "Rust Cracker: HEALTHY"
    else
        log_message "Rust Cracker: UNRESPONSIVE"
    fi
}

# Check database connection
check_database() {
    if command_exists docker && docker ps | grep -q postgres; then
        # Check if we can connect to PostgreSQL
        if docker exec -it postgres pg_isready >/dev/null 2>&1; then
            log_message "PostgreSQL: CONNECTED"
        else
            send_alert "POSTGRESQL CONNECTION FAILED"
        fi
    else
        log_message "PostgreSQL: NOT RUNNING"
    fi
}

# Check Redis connection
check_redis() {
    if command_exists docker && docker ps | grep -q redis; then
        # Check if we can ping Redis
        if docker exec -it redis redis-cli ping | grep -q PONG; then
            log_message "Redis: CONNECTED"
        else
            send_alert "REDIS CONNECTION FAILED"
        fi
    else
        log_message "Redis: NOT RUNNING"
    fi
}

# Monitor API response times
monitor_api_performance() {
    # Measure API response time
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:5000/health 2>/dev/null || echo 999)
    
    if (( $(echo "$response_time > 5" | bc -l) )); then
        send_alert "HIGH API LATENCY: ${response_time}s"
    else
        log_message "API Response Time: ${response_time}s"
    fi
}

# Check error logs
check_error_logs() {
    # Check application logs for errors in the last 5 minutes
    local error_count=0
    
    if [ -d "/app/logs" ]; then
        # This assumes logs are stored in /app/logs
        error_count=$(find /app/logs -name "*.log" -mmin -5 -exec grep -i "error\|exception\|critical" {} \; | wc -l)
    fi
    
    if [ "$error_count" -gt 0 ]; then
        send_alert "ERRORS DETECTED IN LOGS: $error_count errors found"
    fi
}

# Generate performance report
generate_report() {
    log_message "=== SYSTEM MONITORING REPORT ==="
    log_message "Timestamp: $(date)"
    
    check_system_resources
    check_containers
    check_service_health
    check_database
    check_redis
    monitor_api_performance
    check_error_logs
    
    log_message "================================"
    log_message ""
}

# Continuous monitoring function
continuous_monitoring() {
    log_message "Starting continuous monitoring..."
    
    while true; do
        generate_report
        sleep 60  # Monitor every minute
    done
}

# Single check function
single_check() {
    log_message "Running single monitoring check..."
    generate_report
}

# Help function
show_help() {
    echo "CyberCrackPro Monitoring Script"
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  --check     Run a single monitoring check"
    echo "  --start     Start continuous monitoring"
    echo "  --status    Show current system status"
    echo "  --alerts    Show recent alerts"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "Configuration:"
    echo "  Set ALERT_EMAIL to receive email alerts"
    echo "  Set ALERT_WEBHOOK to send webhook notifications"
}

# Show system status
show_status() {
    echo "=== CyberCrackPro System Status ==="
    echo "Date: $(date)"
    
    if command_exists docker; then
        echo "Active Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
    fi
    
    # System resources
    echo "System Resources:"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
    echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", ($3/$2) * 100.0)}')"
    echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
    echo ""
    
    # Service status
    echo "Service Health:"
    if curl -f -s http://localhost:5000/health >/dev/null 2>&1; then
        echo "  Main API: HEALTHY"
    else
        echo "  Main API: UNRESPONSIVE"
    fi
    
    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
        echo "  Go Analyzer: HEALTHY"
    else
        echo "  Go Analyzer: UNRESPONSIVE"
    fi
    
    echo ""
    echo "Latest logs:"
    if [ -f "$LOG_FILE" ]; then
        tail -n 10 "$LOG_FILE"
    else
        echo "  No monitoring log file found"
    fi
}

# Show recent alerts
show_alerts() {
    echo "Recent Alerts:"
    if [ -f "$LOG_FILE" ]; then
        grep -i "alert" "$LOG_FILE" | tail -n 10
    else
        echo "  No monitoring log file found"
    fi
}

# Main script execution
case "${1:-}" in
    --check)
        single_check
        ;;
    --start)
        continuous_monitoring
        ;;
    --status)
        show_status
        ;;
    --alerts)
        show_alerts
        ;;
    --help|-h)
        show_help
        ;;
    *)
        if [ $# -eq 0 ]; then
            show_status
        else
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information."
            exit 1
        fi
        ;;
esac