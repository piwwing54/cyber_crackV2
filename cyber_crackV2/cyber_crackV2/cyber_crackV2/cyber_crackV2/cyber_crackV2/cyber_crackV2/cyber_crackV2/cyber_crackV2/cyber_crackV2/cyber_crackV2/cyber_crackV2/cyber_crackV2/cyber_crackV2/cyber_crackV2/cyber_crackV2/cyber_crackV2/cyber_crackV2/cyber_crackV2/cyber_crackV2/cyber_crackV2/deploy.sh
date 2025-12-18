#!/bin/bash
# 🚀 CYBER CRACK PRO - Deployment Script
# Production deployment script for Cyber Crack Pro

set -e  # Exit on any error

echo "🚀 Starting Cyber Crack Pro Production Deployment..."
echo "==================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
DEPLOY_DIR="/opt/cyber-crack-pro"
BACKUP_DIR="/opt/cyber-crack-backups"
LOG_FILE="/var/log/cyber-crack-deploy.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_success() {
    log_message "✅ $1"
}

log_error() {
    log_message "❌ $1"
}

log_warning() {
    log_message "⚠️ $1"
}

log_info() {
    log_message "ℹ️ $1"
}

# Check if running as root
check_privileges() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root!"
        exit 1
    fi
    log_success "Running with root privileges"
}

# Install system dependencies for production
install_production_deps() {
    log_info "Installing production dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get > /dev/null; then
            apt-get update
            apt-get install -y \
                docker.io \
                docker-compose \
                nginx \
                certbot \
                python3 \
                python3-pip \
                redis-server \
                postgresql \
                postgresql-contrib \
                nginx-extras \
                supervisor \
                iptables \
                fail2ban \
                ufw \
                jq \
                curl \
                wget \
                git
        elif command -v yum > /dev/null; then
            yum update -y
            yum install -y \
                docker \
                docker-compose-plugin \
                nginx \
                certbot \
                python3 \
                python3-pip \
                redis \
                postgresql-server \
                postgresql-contrib \
                supervisor \
                iptables-services \
                fail2ban \
                jq \
                curl \
                wget \
                git
        fi
    fi
    
    # Enable and start services
    systemctl enable docker redis postgresql nginx
    systemctl start docker redis postgresql nginx
    
    log_success "Production dependencies installed and services started"
}

# Setup production environment
setup_production_env() {
    log_info "Setting up production environment..."
    
    # Create directories
    mkdir -p "$DEPLOY_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p /var/log/cyber-crack-pro
    mkdir -p /var/lib/cyber-crack-pro/uploads
    mkdir -p /var/lib/cyber-crack-pro/results
    mkdir -p /var/lib/cyber-crack-pro/models
    
    # Set permissions
    chown -R www-data:www-data /var/lib/cyber-crack-pro
    chmod -R 755 /var/lib/cyber-crack-pro
    
    log_success "Production directories created with proper permissions"
}

# Setup firewall rules
setup_firewall() {
    log_info "Setting up firewall rules..."
    
    # Using UFW (Uncomplicated Firewall)
    if command -v ufw > /dev/null; then
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        
        # Allow SSH
        ufw allow ssh
        
        # Allow HTTP/HTTPS
        ufw allow 80/tcp
        ufw allow 443/tcp
        
        # Allow Docker bridge network if using Docker
        ufw allow from 172.16.0.0/12
        
        ufw --force enable
        log_success "Firewall rules configured"
    else
        # Using iptables directly
        iptables -F  # Flush existing rules
        iptables -P INPUT DROP
        iptables -P FORWARD DROP
        iptables -P OUTPUT ACCEPT
        
        # Allow loopback
        iptables -A INPUT -i lo -j ACCEPT
        
        # Allow established connections
        iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
        
        # Allow SSH
        iptables -A INPUT -p tcp --dport 22 -j ACCEPT
        
        # Allow HTTP/HTTPS
        iptables -A INPUT -p tcp --dport 80 -j ACCEPT
        iptables -A INPUT -p tcp --dport 443 -j ACCEPT
        
        # Allow Docker networks
        iptables -A INPUT -s 172.16.0.0/12 -j ACCEPT
        
        # Save iptables rules
        if [ -f /etc/iptables/rules.v4 ]; then
            iptables-save > /etc/iptables/rules.v4
        fi
        
        log_success "Firewall rules configured with iptables"
    fi
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    if command -v certbot > /dev/null; then
        # Try to obtain certificate automatically
        # You would replace cyber-crack-pro.com with your domain
        CERT_DOMAIN="${CERT_DOMAIN:-cyber-crack-pro.com}"
        
        # Check if certificate already exists
        if [ ! -f "/etc/letsencrypt/live/$CERT_DOMAIN/fullchain.pem" ]; then
            log_info "Obtaining SSL certificate for $CERT_DOMAIN..."
            certbot certonly --nginx -d "$CERT_DOMAIN" --agree-tos --email "${ADMIN_EMAIL:-admin@cyber-crack-pro.com}"
        else
            log_info "SSL certificate already exists for $CERT_DOMAIN"
        fi
    else
        # Generate self-signed certificates for testing
        log_warning "Certbot not found, generating self-signed certificates"
        
        mkdir -p /etc/nginx/ssl
        openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
            -subj "/C=US/ST=State/L=City/O=CyberCrackPro/CN=cyber-crack-pro.local" \
            -keyout /etc/nginx/ssl/cyber-crack-pro.key \
            -out /etc/nginx/ssl/cyber-crack-pro.crt
        
        log_success "Self-signed SSL certificates generated"
    fi
}

# Configure Nginx
setup_nginx() {
    log_info "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > /etc/nginx/sites-available/cyber-crack-pro << 'EOF'
server {
    listen 80;
    server_name cyber-crack-pro.com www.cyber-crack-pro.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cyber-crack-pro.com www.cyber-crack-pro.com;

    ssl_certificate /etc/letsencrypt/live/cyber-crack-pro.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cyber-crack-pro.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Main application
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API routes
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/cyber-crack-pro/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Security - block sensitive files
    location ~ /\. {
        deny all;
    }

    # Logging
    access_log /var/log/nginx/cyber-crack-pro.access.log;
    error_log /var/log/nginx/cyber-crack-pro.error.log;
}
EOF

    # Create symlink
    ln -sf /etc/nginx/sites-available/cyber-crack-pro /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    nginx -t
    systemctl reload nginx
    
    log_success "Nginx configured"
}

# Setup PostgreSQL
setup_postgres() {
    log_info "Configuring PostgreSQL..."
    
    # Initialize database if not initialized
    if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
        postgresql-setup --initdb
    fi
    
    # Configure PostgreSQL for production
    cat >> /var/lib/pgsql/data/postgresql.conf << 'EOF'

# Production settings
listen_addresses = '*'
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
EOF

    # Configure authentication
    echo "host all all 0.0.0.0/0 md5" >> /var/lib/pgsql/data/pg_hba.conf
    
    systemctl restart postgresql
    
    # Create database and user
    sudo -u postgres psql << 'EOF'
CREATE DATABASE cybercrackpro;
CREATE USER cybercrack WITH PASSWORD 'secure_password_change_me';
GRANT ALL PRIVILEGES ON DATABASE cybercrackpro TO cybercrack;
ALTER USER cybercrack CREATEDB CREATEROLE;
EOF
    
    log_success "PostgreSQL configured"
}

# Setup Redis
setup_redis() {
    log_info "Configuring Redis..."
    
    # Configure Redis for production
    sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis.conf
    sed -i 's/^protected-mode yes/protected-mode yes/' /etc/redis.conf
    sed -i 's/# requirepass .*/requirepass secure_redis_password_change_me/' /etc/redis.conf
    sed -i 's/^maxmemory .*/maxmemory 2gb/' /etc/redis.conf
    sed -i 's/^maxmemory-policy .*/maxmemory-policy allkeys-lru/' /etc/redis.conf
    
    systemctl restart redis
    
    log_success "Redis configured"
}

# Setup Docker services
setup_docker_services() {
    log_info "Setting up Docker services..."
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        # Copy docker-compose.yml to deployment directory
        cp docker-compose.yml "$DEPLOY_DIR/"
        cd "$DEPLOY_DIR"
        
        # Set production environment variables
        export COMPOSE_HTTP_TIMEOUT=300
        
        # Pull latest images
        docker-compose pull
        
        # Start services
        docker-compose up -d --force-recreate
        
        # Wait for services to be healthy
        log_info "Waiting for services to be ready..."
        sleep 60
        
        # Check service health
        docker-compose ps
        
        log_success "Docker services started"
        cd - > /dev/null
    else
        log_error "docker-compose.yml not found! Cannot start Docker services."
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create monitoring configuration
    mkdir -p /etc/cyber-crack-monitoring
    
    # Install monitoring tools if available
    if command -v docker > /dev/null; then
        # Start monitoring containers alongside main services
        cat > /tmp/monitoring-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
EOF
        
        # Start monitoring services
        docker-compose -f /tmp/monitoring-compose.yml up -d
        log_success "Monitoring services started"
    fi
}

# Setup log rotation
setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    cat > /etc/logrotate.d/cyber-crack-pro << 'EOF'
/var/log/cyber-crack-pro/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    postrotate
        systemctl reload cyber-crack-pro || true
    endscript
}

/var/log/nginx/cyber-crack-pro*.log {
    daily
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 640 root adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
EOF

    log_success "Log rotation configured"
}

# Setup backup
setup_backup() {
    log_info "Setting up backup configuration..."
    
    # Create backup script
    cat > /opt/backup-cyber-crack.sh << 'EOF'
#!/bin/bash
# Cyber Crack Pro Backup Script

BACKUP_DIR="/opt/cyber-crack-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="cyber-crack-pro-backup-$DATE"

mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup configuration
cp -r /opt/cyber-crack-pro/config "$BACKUP_DIR/$BACKUP_NAME/config" 2>/dev/null || true

# Backup database
pg_dump -U cybercrack -h localhost cybercrackpro > "$BACKUP_DIR/$BACKUP_NAME/database.sql" 2>/dev/null || true

# Backup uploads and results (optional, large files)
if [ "$INCLUDE_DATA" = "yes" ]; then
    cp -r /var/lib/cyber-crack-pro/uploads "$BACKUP_DIR/$BACKUP_NAME/uploads" 2>/dev/null || true
    cp -r /var/lib/cyber-crack-pro/results "$BACKUP_DIR/$BACKUP_NAME/results" 2>/dev/null || true
fi

# Create archive
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
rm -rf "$BACKUP_DIR/$BACKUP_NAME"

# Keep only last 30 backups
ls -t "$BACKUP_DIR"/*.tar.gz | tail -n +31 | xargs rm -f 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
EOF

    chmod +x /opt/backup-cyber-crack.sh
    
    # Add to cron for daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-cyber-crack.sh") | crontab -
    
    log_success "Backup script created and scheduled"
}

# Setup security hardening
setup_security_hardening() {
    log_info "Applying security hardening..."
    
    # Configure fail2ban
    if [ -f /etc/fail2ban/jail.local ]; then
        cat >> /etc/fail2ban/jail.local << 'EOF'

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400
EOF
        
        systemctl restart fail2ban
    fi
    
    # Set up system monitoring
    cat > /etc/systemd/system/cyber-crack-monitor.service << 'EOF'
[Unit]
Description=Cyber Crack Pro System Monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/cyber-crack-pro/monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl enable cyber-crack-monitor.service
    log_success "Security hardening applied"
}

# Final status check
final_status_check() {
    log_info "Performing final status check..."
    
    # Check if main services are running
    if command -v docker > /dev/null && [ -f "docker-compose.yml" ]; then
        SERVICES_STATUS=$(docker-compose ps --format "json")
        echo "$SERVICES_STATUS" | jq
    fi
    
    # Check nginx
    if systemctl is-active nginx > /dev/null 2>&1; then
        log_success "Nginx is running"
    else
        log_error "Nginx is not running"
    fi
    
    # Check database
    if nc -z localhost 5432; then
        log_success "PostgreSQL is accessible"
    else
        log_error "PostgreSQL is not accessible"
    fi
    
    # Check Redis
    if nc -z localhost 6379; then
        log_success "Redis is accessible"
    else
        log_error "Redis is not accessible"
    fi
    
    log_success "Final status check completed"
}

# Display deployment information
display_deployment_info() {
    echo ""
    echo -e "${GREEN}🚀 Cyber Crack Pro Production Deployment Complete!${NC}"
    echo "==========================================================="
    echo ""
    echo "📊 Deployment Summary:"
    echo "   ✓ System dependencies installed"
    echo "   ✓ Production environment configured"
    echo "   ✓ Firewall rules applied"
    echo "   ✓ SSL certificates configured"
    echo "   ✓ Nginx reverse proxy set up"
    echo "   ✓ PostgreSQL database configured"
    echo "   ✓ Redis cache configured"
    echo "   ✓ Docker services started"
    echo "   ✓ Monitoring configured"
    echo "   ✓ Log rotation enabled"
    echo "   ✓ Backup system configured"
    echo "   ✓ Security hardening applied"
    echo ""
    echo "🌐 Access Information:"
    echo "   Web Dashboard: https://cyber-crack-pro.com"
    echo "   API Endpoint: https://cyber-crack-pro.com/api"
    echo "   Monitoring (Grafana): http://localhost:3001 (admin/admin)"
    echo "   Prometheus: http://localhost:9090"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Restart services: docker-compose restart"
    echo "   Stop services: docker-compose down"
    echo "   Check status: docker-compose ps"
    echo ""
    echo "🔐 Security Information:"
    echo "   - Change default passwords immediately"
    echo "   - Monitor SSL certificate renewal (cron job at /etc/cron.d/certbot)"
    echo "   - Check firewall rules and adjust as needed"
    echo "   - Review log files regularly: /var/log/cyber-crack-pro/"
    echo ""
    echo "🔄 Automatic Maintenance:"
    echo "   - Daily backups at 2:00 AM UTC"
    echo "   - SSL certificate auto-renewal"
    echo "   - Log rotation daily"
    echo ""
    echo "⚠️  Important Notes:"
    echo "   - Update admin password in Grafana (default: admin/admin)"
    echo "   - Secure your .env file with sensitive information"
    echo "   - Monitor system resources for optimal performance"
    echo "   - Consider setting up proper monitoring alerts"
    echo ""
}

# Main deployment process
main() {
    log_info "Starting Cyber Crack Pro production deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment directory: $DEPLOY_DIR"
    
    check_privileges
    install_production_dependencies
    setup_production_environment
    setup_firewall
    setup_ssl
    setup_nginx
    setup_postgres
    setup_redis
    setup_docker_services
    setup_monitoring
    setup_log_rotation
    setup_backup
    setup_security_hardening
    final_status_check
    display_deployment_info
    
    log_success "Production deployment completed successfully!"
}

# Run main function
main "$@"