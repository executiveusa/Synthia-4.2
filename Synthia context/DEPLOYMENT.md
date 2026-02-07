# Synthia Deployment Guide - Hostinger VPS

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/synthia.git
cd synthia

# 2. Copy environment configuration
cp master.env .env

# 3. Update .env with your actual credentials
nano .env

# 4. Start all services
docker-compose up -d

# 5. Verify deployment
docker ps
curl http://localhost:8000/health
curl http://localhost:5173

# 6. Access Synthia
open http://localhost:5173
```

## Hostinger VPS Setup

### Prerequisites

**Minimum Requirements:**
- Hostinger VPS Plan: Business or higher
- RAM: 8GB minimum (16GB recommended)
- Storage: 100GB SSD
- CPU: 4 cores minimum
- OS: Ubuntu 24.04 LTS

### Initial Server Setup

```bash
# SSH into your Hostinger VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Create synthia user
adduser synthia
usermod -aG docker synthia
usermod -aG sudo synthia

# Switch to synthia user
su - synthia
```

### Clone and Configure

```bash
# Clone Synthia
git clone https://github.com/yourusername/synthia.git
cd synthia

# Set up environment
cp master.env .env

# CRITICAL: Update these in .env
nano .env
# Update:
# - ANTHROPIC_API_KEY (your actual key)
# - OPENAI_API_KEY (if using)
# - HOSTINGER_API_TOKEN (from Hostinger panel)
# - ELEVEN_LABS_API (for voice)
# - HEY_GEN_API (for avatars)
# - SUPABASE_* (all Supabase credentials)
# - STRIPE_* (if handling payments)

# Set permissions
chmod 600 .env
```

### SSL and Domain Setup

```bash
# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/synthia

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name synthia.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Voice endpoints
    location /voice {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }

    # WebSocket for real-time updates
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/synthia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d synthia.yourdomain.com

# Verify SSL auto-renewal
sudo certbot renew --dry-run
```

### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  synthia-backend:
    build: ./backend
    container_name: synthia-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    env_file:
      - .env
    volumes:
      - ./backend:/app
      - ./skills:/app/skills
      - ./design-system:/app/design-system
      - ./.mcp-agent-mail:/app/.mcp-agent-mail
      - ./.beads:/app/.beads
      - ./agent-lightning/reports:/app/reports
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - ollama
    networks:
      - synthia-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  synthia-frontend:
    build: ./frontend
    container_name: synthia-frontend
    restart: unless-stopped
    ports:
      - "5173:5173"
    env_file:
      - .env
    volumes:
      - ./frontend:/app
      - /app/node_modules
    stdin_open: true
    tty: true
    depends_on:
      - synthia-backend
    networks:
      - synthia-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5173"]
      interval: 30s
      timeout: 10s
      retries: 3

  synthia-agent-lightning:
    build: ./agent-lightning
    container_name: synthia-agent-lightning
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - BACKEND_URL=http://synthia-backend:8000
    env_file:
      - .env
    volumes:
      - ./agent-lightning:/app
      - ./learning-reports:/app/reports
    depends_on:
      - synthia-backend
    networks:
      - synthia-network

  ollama:
    image: ollama/ollama:latest
    container_name: synthia-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - synthia-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    container_name: synthia-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - synthia-network
    command: redis-server --appendonly yes

volumes:
  ollama-data:
  redis-data:

networks:
  synthia-network:
    driver: bridge
```

### Launch Services

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker ps

# Verify health
curl http://localhost:8000/health
# Should return: {"status": "healthy", "version": "1.0.0"}

curl http://localhost:5173
# Should return HTML
```

### Ollama Model Setup

```bash
# Pull required models
docker exec -it synthia-ollama ollama pull llama3.2
docker exec -it synthia-ollama ollama pull codellama
docker exec -it synthia-ollama ollama pull mistral

# Verify models
docker exec -it synthia-ollama ollama list
```

## Monitoring and Maintenance

### Health Checks

Create `/root/monitor-synthia.sh`:

```bash
#!/bin/bash

# Check if services are running
services=("synthia-backend" "synthia-frontend" "synthia-agent-lightning" "synthia-ollama")

for service in "${services[@]}"; do
    if ! docker ps | grep -q "$service"; then
        echo "⚠️  $service is down!"
        docker-compose restart "$service"
        
        # Send alert (configure with your notification service)
        curl -X POST https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage \
          -d chat_id=YOUR_CHAT_ID \
          -d text="Synthia Alert: $service restarted on $(hostname)"
    fi
done

# Check disk space
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    echo "⚠️  Disk usage at ${disk_usage}%"
    # Cleanup old Docker images
    docker image prune -af --filter "until=168h"
fi
```

```bash
# Make executable
chmod +x /root/monitor-synthia.sh

# Add to crontab (check every 5 minutes)
crontab -e
# Add:
*/5 * * * * /root/monitor-synthia.sh >> /var/log/synthia-monitor.log 2>&1
```

### Daily Backups

Create `/root/backup-synthia.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/synthia"
DATE=$(date +%Y-%m-%d)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup code and configs
tar -czf "$BACKUP_DIR/synthia-code-$DATE.tar.gz" \
  /home/synthia/synthia \
  --exclude="node_modules" \
  --exclude=".git"

# Backup Docker volumes
docker run --rm \
  -v ollama-data:/data \
  -v "$BACKUP_DIR:/backup" \
  alpine tar -czf "/backup/ollama-data-$DATE.tar.gz" /data

# Upload to Supabase storage (if configured)
# curl -X POST https://kbphngxqozmpfrbdzgca.supabase.co/storage/v1/object/backups/synthia-$DATE.tar.gz ...

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
```

```bash
chmod +x /root/backup-synthia.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add:
0 2 * * * /root/backup-synthia.sh >> /var/log/synthia-backup.log 2>&1
```

### Log Management

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/synthia

# Add:
/var/log/synthia-*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}

# View recent logs
docker-compose logs --tail=100 -f synthia-backend
docker-compose logs --tail=100 -f synthia-frontend
docker-compose logs --tail=100 -f synthia-agent-lightning
```

## Performance Optimization

### Enable Cloudflare

1. Point your domain DNS to Cloudflare
2. Enable:
   - Auto-minify (JS, CSS, HTML)
   - Brotli compression
   - Rocket Loader
   - HTTP/3 (QUIC)
3. Set caching rules:
   - Static assets: Cache everything, edge TTL 7 days
   - API routes: Bypass cache

### Database Optimization

If using Supabase:

```sql
-- Create indexes for common queries
CREATE INDEX idx_designs_created_at ON designs(created_at DESC);
CREATE INDEX idx_designs_user_id ON designs(user_id);
CREATE INDEX idx_components_type ON components(type);

-- Enable row-level security
ALTER TABLE designs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own designs"
  ON designs FOR SELECT
  USING (auth.uid() = user_id);
```

### Caching Strategy

Update backend to use Redis:

```python
# backend/cache.py
import redis
import json

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_cached(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cached(key, value, ttl=3600):
    redis_client.setex(key, ttl, json.dumps(value))
```

## Security Hardening

### Firewall Rules

```bash
# Install UFW
sudo apt install ufw -y

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Fail2Ban for SSH

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Configure
sudo nano /etc/fail2ban/jail.local

# Add:
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600

# Restart
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

### Environment Security

```bash
# Ensure .env is not world-readable
chmod 600 .env

# Add to .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore

# Rotate API keys monthly
# Set reminder: first day of each month
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs synthia-backend

# Common issues:
# 1. Port already in use
sudo lsof -i :8000
sudo lsof -i :5173

# 2. Missing environment variables
docker-compose config

# 3. Permission errors
sudo chown -R synthia:synthia /home/synthia/synthia
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Limit container memory
# Add to docker-compose.yml under each service:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Slow Response Times

```bash
# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Check backend health
curl http://localhost:8000/health

# Monitor network
docker network inspect synthia-network

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

## Updating Synthia

```bash
# Pull latest changes
cd /home/synthia/synthia
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Verify
docker ps
curl http://localhost:8000/health
```

## Agent Lightning Dashboard

Access at: `http://synthia.yourdomain.com:8001`

**Features:**
- Daily learning reports from Awwwards
- Performance metrics per skill
- Agent coordination efficiency
- Error tracking and debugging

## Support Resources

**Documentation:**
- UDIP v2.1 ULTIMATE: `/UDIP-v2_1-ULTIMATE-SYSTEM-PROMPT.md`
- Skills Index: `/skills-index.md`
- Individual Skills: `/skills/*.md`

**Community:**
- GitHub Issues: Report bugs and feature requests
- Discord: Join Synthia community (link in README)

**Commercial Support:**
- Email: support@synthia.design
- Priority response for Pro users

---

**Synthia v1.0 - Hostinger Deployment Guide**  
**Last Updated:** 2026-02-07  
**Status:** ✅ PRODUCTION READY
