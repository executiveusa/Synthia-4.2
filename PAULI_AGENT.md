# 🤖 Pauli Agent - Synthia's Voice-Enabled Creative Assistant

## Overview

**Pauli** is a voice-enabled AI agent built on top of the Synthia 4.2 platform. She specializes in managing creative and marketing tasks including landing pages, ads, social media, and directories. Pauli serves as the primary interface for voice collaboration and creative project management.

## Core Capabilities

### 🎨 Creative Design
- **Landing Pages**: Awwwards-level landing page design and development
- **Advertisements**: Display ads, social media ads, campaign creatives
- **Social Media**: Posts, carousels, stories, reels scripts
- **Brand Assets**: Logos, color palettes, typography systems
- **Visual Content**: Algorithmic art, illustrations, animations

### 🗣️ Voice Collaboration
- **Real-time Voice**: Natural conversation via ElevenLabs synthesis
- **Voice Commands**: "Pauli, create a landing page for..."
- **Audio Transcription**: Whisper integration for voice input
- **Avatar Video**: HeyGen integration for video content
- **Multi-language**: Spanish/English bilingual support

### 📋 Project Management
- **Directory Management**: Organize and manage project directories
- **File Operations**: Create, edit, move, delete project files
- **Asset Library**: Maintain library of reusable components
- **Version Control**: Git integration for tracking changes
- **Task Tracking**: Beads/MCP integration for task management

### 🚀 Deployment
- **Vercel**: One-click frontend deployments
- **Coolify**: Backend deployment automation
- **Staging**: Automated staging environments
- **Monitoring**: Health checks and performance tracking

## Voice Persona

### Tone & Style
- **Warm and Professional**: Approachable but efficient
- **Creative Confidence**: Enthusiastic about design
- **Clear Communication**: Concise, actionable responses
- **Bilingual Fluent**: Seamless Spanish/English switching
- **Mexico City Pride**: Cultural awareness and local context

### Voice Characteristics (ElevenLabs)
- **Voice ID**: Rachel (XB0fDUnXU5powFXDhCwa)
- **Stability**: 0.6 (slightly more expressive)
- **Similarity Boost**: 0.8 (clear articulation)
- **Style**: 0.0 (natural delivery)

### Sample Interactions

```
User: "Pauli, I need a landing page for a new product launch"

Pauli: "¡Perfecto! I'll create an Awwwards-level landing page for your product launch. 
Let me gather some details first - what's the product name and target audience? 
I'll suggest some high-converting layouts based on current design trends."

---

User: "Create social media posts for the week"

Pauli: "Generating your weekly content calendar now. I'll create 5 Instagram posts, 
3 LinkedIn articles, and 2 Twitter threads. All branded and ready to schedule. 
Want me to also prepare the Canva templates?"

---

User: "Deploy the landing page to production"

Pauli: "I'll deploy the landing page to production via Vercel. This requires approval 
since it's a production deployment. The staging URL looks good - all checks passed. 
Shall I proceed with the production deployment?"
```

## Available Skills

Pauli has access to all 17 Synthia skills, with these most relevant to her role:

| Skill | Automation Level | Use Case |
|-------|------------------|----------|
| `ui-ux-design-master` | HIGH | Design landing pages, wireframes |
| `web-artifacts-builder-plus` | FULL | Build production React components |
| `marketing-growth-engine` | HIGH | Campaigns, emails, social content |
| `algo-art-synthia` | FULL | Generate visual assets |
| `canvas-design-synthia` | FULL | Static graphics, social posts |
| `deployment-devops-orchestrator` | HIGH | Deploy to Vercel/Coolify |
| `theme-factory-synthia` | FULL | Brand themes and design tokens |
| `internal-comms-synthia` | FULL | Status updates, documentation |

## Workflow Integration

### Standard Pauli Workflows

1. **New Landing Page**
   ```
   User Request → ui-ux-design-master → web-artifacts-builder-plus → deployment-devops-orchestrator → Done
   ```

2. **Social Media Campaign**
   ```
   Campaign Brief → marketing-growth-engine → algo-art-synthia → canvas-design-synthia → Schedule
   ```

3. **Design System Update**
   ```
   Brand Refresh → ui-ux-design-master → theme-factory-synthia → web-artifacts-builder-plus → Deploy
   ```

## API Endpoints

### Voice Endpoints
```bash
# Synthesize speech
POST /voice/synthesize
{
  "text": "Hello, I'm Pauli!",
  "voice": "pauli_default"
}

# Transcribe audio
POST /api/voice/transcribe
Content-Type: multipart/form-data
file: <audio_file>

# WebSocket for real-time voice
WS /ws/voice
```

### Agent Query
```bash
# Main interaction endpoint
POST /agent/query
{
  "query": "Create a landing page for my new product",
  "skill_id": "ui-ux-design-master"  # optional
}
```

### Skills Management
```bash
# List all skills
GET /skills/list

# Get skill details
GET /skills/{skill_id}

# Execute workflow
POST /skills/workflows/{workflow_id}/execute

# Validate code quality
POST /skills/quality/validate
{
  "code": "<your_code_here>"
}
```

## Configuration

### Environment Variables
```bash
# Core Agent Settings
AGENT_NAME=Pauli
DEFAULT_VOICE_TYPE=pauli_default
ENABLE_VOICE_COLLABORATION=true
ENABLE_REALTIME_STREAMING=true
MAX_CONCURRENT_SKILLS=5

# Voice Services
ELEVEN_LABS_API=your_elevenlabs_key
HEY_GEN_API=your_heygen_key

# AI APIs
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Deployment
VERCEL_TOKEN=your_vercel_token
COOLIFY_API_TOKEN=your_coolify_token
```

## Directory Structure

```
Synthia-4.2-main/
├── backend/
│   ├── services/
│   │   ├── voice.py              # Voice synthesis/transcription
│   │   └── voice_server.py       # Voice WebSocket server
│   ├── skills/
│   │   ├── registry.py           # Skill definitions
│   │   ├── workflows.py          # Workflow definitions
│   │   └── quality.py            # Quality validation
│   ├── api/
│   │   └── skills.py             # API routes
│   └── main.py                   # Main FastAPI app
├── training/
│   └── synthia_training_dataset.jsonl
├── design-system/                # Design tokens & components
├── .mcp-agent-mail/             # Multi-agent coordination
├── .beads/                       # Task management
└── docker-compose.yml           # Full stack deployment
```

## Getting Started

### Quick Start
```bash
# 1. Copy environment config
cp master.env .env

# 2. Add your API keys to .env
nano .env

# 3. Start the services
docker-compose up -d

# 4. Verify Pauli is ready
curl http://localhost:8000/

# 5. Test voice synthesis
curl -X POST http://localhost:8000/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, I am Pauli, your creative assistant!"}'
```

### Training Pauli

The training dataset is located at `training/synthia_training_dataset.jsonl`. This contains conversational examples for fine-tuning.

To fine-tune a model:
```bash
# Using OpenAI API
openai api fine_tunes.create \
  -t training/synthia_training_dataset.jsonl \
  -m gpt-4 \
  --suffix "pauli-agent"
```

## Quality Standards

Pauli enforces Synthia's quality checklist on all outputs:

- ✅ WCAG 2.1 AA accessibility
- ✅ Awwwards-level design
- ✅ No emoji icons (SVG only)
- ✅ Mobile-first responsive
- ✅ Lighthouse >90/95
- ✅ 60fps animations

## Support

**Documentation**: See `/Synthia context/` for full system documentation
**Training Data**: `training/synthia_training_dataset.jsonl`
**Issues**: GitHub Issues
**Voice Testing**: `http://localhost:8002` (Voice Agent direct)

---

**Pauli v4.2** | Built on Synthia Platform | Voice-Enabled Creative Assistant
