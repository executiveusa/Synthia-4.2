# 🚀 Synthia 4.2 / Pauli Agent - Complete Setup Guide

## Prerequisites

### System Requirements
- **OS**: Ubuntu 24.04 LTS (recommended) or Windows 11 with WSL2
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 100GB SSD
- **CPU**: 4 cores minimum (8+ recommended)
- **GPU**: NVIDIA GPU optional but recommended for Ollama

### Required Accounts
- [ ] Anthropic (Claude API)
- [ ] OpenAI (Whisper + GPT-4 fallback)
- [ ] ElevenLabs (Voice synthesis)
- [ ] HeyGen (Avatar video)
- [ ] Supabase (Database)
- [ ] Vercel (Frontend deployment)
- [ ] Coolify or Hostinger VPS (Backend deployment)

## Step-by-Step Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/synthia.git
cd Synthia-4.2-main
```

### 2. Environment Configuration
```bash
# Copy template
cp master.env .env

# Edit with your API keys
nano .env
```

**Required minimum keys:**
```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ELEVEN_LABS_API=your_key_here
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
```

### 3. Docker Installation

**Ubuntu:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**Windows (WSL2):**
```bash
# Docker Desktop should be installed
# Enable WSL2 backend in Docker Desktop settings
```

### 4. Start Services
```bash
# Build and start all services
docker-compose up -d --build

# Verify services are running
docker ps

# Check logs
docker-compose logs -f backend
```

### 5. Pull Ollama Models
```bash
# Wait for Ollama to start
sleep 10

# Pull required models
docker exec -it synthia-ollama ollama pull moondream
docker exec -it synthia-ollama ollama pull qwen2.5-coder:1.5b
docker exec -it synthia-ollama ollama pull llama3.2

# Verify
docker exec -it synthia-ollama ollama list
```

### 6. Verify Installation
```bash
# Health check
curl http://localhost:8000/health

# System info
curl http://localhost:8000/

# List skills
curl http://localhost:8000/skills/list

# Test voice (requires ElevenLabs API key)
curl -X POST http://localhost:8000/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Pauli is online and ready!"}' \
  --output test.mp3
```

## Development Workflow

### Local Development
```bash
# Start only backend and dependencies
docker-compose up -d backend redis ollama

# Run backend in development mode
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Voice Agent Development
```bash
# Voice service runs on port 8002
# Test WebSocket connection
wscat -c ws://localhost:8002/ws/voice

# Or use the voice server directly
python -m services.voice_server
```

## Production Deployment

### Hostinger VPS Deployment

1. **Provision VPS**
   - Business plan or higher
   - Ubuntu 24.04 LTS
   - 8GB RAM, 4 cores

2. **Server Setup**
```bash
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose-plugin -y

# Create synthia user
adduser synthia
usermod -aG docker synthia
su - synthia
```

3. **Deploy Synthia**
```bash
git clone https://github.com/yourusername/synthia.git
cd synthia
cp master.env .env
# Edit .env with production keys
nano .env

docker-compose up -d
```

4. **SSL & Domain**
```bash
# Install Nginx + Certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
cat > /etc/nginx/sites-available/synthia << 'EOF'
server {
    listen 80;
    server_name pauli.yourdomain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /voice {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/synthia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d pauli.yourdomain.com
```

## API Usage Examples

### Generate Landing Page
```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a landing page for a Mexico City coffee shop",
    "skill_id": "ui-ux-design-master"
  }'
```

### Execute Marketing Workflow
```bash
curl -X POST http://localhost:8000/skills/workflows/social-media-campaign/execute
```

### Validate Code Quality
```bash
curl -X POST http://localhost:8000/skills/quality/validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "<button onClick={handleClick}>Click me</button>"
  }'
```

### Image to Code
```bash
curl -X POST http://localhost:8000/generate \
  -F "file=@screenshot.png" \
  -F "vision_model=moondream" \
  -F "code_model=qwen2.5-coder:1.5b"
```

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Check ports
sudo lsof -i :8000
sudo lsof -i :5173
sudo lsof -i :11434

# Restart services
docker-compose down
docker-compose up -d
```

### Ollama Issues
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull models manually
docker exec -it synthia-ollama ollama pull llama3.2

# Check GPU support
docker exec -it synthia-ollama nvidia-smi
```

### Voice Service Issues
```bash
# Test voice service directly
curl http://localhost:8002/health

# Check ElevenLabs API key
curl -H "xi-api-key: $ELEVEN_LABS_API" \
  https://api.elevenlabs.io/v1/voices
```

### Quality Validation Errors
```bash
# Test quality check
curl -X POST http://localhost:8000/skills/quality/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "<div>Hello</div>"}'
```

## Monitoring

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Voice Agent
curl http://localhost:8002/health

# Ollama
curl http://localhost:11434/api/tags

# Redis
redis-cli ping
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f voice-agent
docker-compose logs -f celery-worker
```

### Performance Monitoring
```bash
# Container stats
docker stats

# Resource usage
docker system df
```

## Training & Fine-tuning

### Using Training Dataset
```bash
# Verify training data
curl http://localhost:8000/training/dataset

# Fine-tune with OpenAI
openai api fine_tunes.create \
  -t training/synthia_training_dataset.jsonl \
  -m gpt-4 \
  --suffix "pauli-v4.2"
```

### Adding New Training Examples
```bash
# Edit the training dataset
nano training/synthia_training_dataset.jsonl

# Add new examples in JSONL format:
# {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Security

### Environment Variables
```bash
# Ensure .env is not committed
cat .gitignore | grep .env

# Set proper permissions
chmod 600 .env

# Rotate keys monthly
```

### Firewall
```bash
# UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

## Next Steps

1. ✅ Setup complete
2. 📚 Review `PAULI_AGENT.md` for usage
3. 🎨 Create your first project
4. 🗣️ Test voice collaboration
5. 🚀 Deploy to production

---

**Need Help?**
- Documentation: `/Synthia context/`
- API Docs: `http://localhost:8000/docs`
- Training Data: `training/synthia_training_dataset.jsonl`
