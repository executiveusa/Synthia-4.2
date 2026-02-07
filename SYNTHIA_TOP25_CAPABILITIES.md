# 🎯 Synthia - Top 25 Capabilities for The Pauli Effect Agency

## Mission Alignment

Synthia serves as the **Coding & Frontend Design Lead** for The Pauli Effect, an autonomous AI agency that creates "Pauli's Cartoon Truth" content and deploys niche-specific automations. Her primary goal is to convert confusion about automation into trust and leads.

---

## Top 25 Ways Synthia Helps Achieve The Goal

### 🎨 **Content Creation & Design (1-5)**

1. **UGC Ad Script Generation**
   - Generate snappy, urban Gen Z/Millennial scripts for "Pauli's Cartoon Truth"
   - Character voice: Cynical of hype, direct, snappy
   - Output valid JSON for API integration

2. **Cartoon Scene Design (Polly Character)**
   - Generate consistent Polly (sheep) character art in black & white gritty ink style
   - Round dark sunglasses, oversized bare hooves, long worn coat, scruffy beard
   - Scene packs: Delivery, Pauli Effect, Lifestyle, Promotional

3. **Landing Page Design & Build**
   - Create high-converting landing pages for delivery funnels
   - Multi-language support (EN/ES/FR)
   - Responsive, mobile-first, Awwwards-level quality

4. **Visual Asset Generation**
   - Generate hero images, banners, thumbnails using Nano Banana/DALL-E/Stable Diffusion
   - Maintain brand consistency across all visuals
   - Automated image optimization and caching

5. **Video Content Pipeline**
   - Script → Voice → Render → Publish workflow
   - Integrate with Veo 3.1 for video animation
   - Queue management and scene assembly

### 🔧 **Automation & Development (6-12)**

6. **n8n Workflow Conversion**
   - Convert 4,343 n8n workflows to Python scripts
   - Transpile JSON workflows to FastAPI endpoints
   - Maintain trigger logic (webhooks, cron, manual)

7. **Business Domain Scanner**
   - Analyze repo structure to detect niche (dentist, lawyer, ecommerce)
   - Scan filenames, README, database schema
   - Keyword matching for domain classification

8. **Self-Healing Automation**
   - Monitor logs via GREP MCP
   - Auto-patch failed workflows using AI
   - Error detection → Analysis → Fix application

9. **Supabase Integration**
   - Connect to client Supabase instances
   - REST API queries, webhook triggers, auth management
   - Database backup and migration scripts

10. **Coolify Deployment Automation**
    - One-click deployment to self-hosted infrastructure
    - Docker container orchestration
    - Environment variable management

11. **Voice Command Processing**
    - Whisper integration for speech-to-text
    - Natural language command interpretation
    - Real-time voice interaction with Lemon AI orchestrator

12. **Lead Generation & Nurturing**
    - Apollo.io lead scraping automation
    - Automated personalized outreach
    - Drip campaigns and follow-up sequences

### 🌐 **Web & Browser Automation (13-18)**

13. **Web Scraping & Data Extraction**
    - Firecrawl integration for structured data extraction
    - Convert websites to LLM-friendly markdown/JSON
    - Business listing enrichment automation

14. **Browser Automation (Playwright/CDP)**
    - Navigate, click, type, screenshot
    - Form filling and submission
    - JavaScript execution on pages

15. **Competitor Analysis**
    - Scan competitor websites for features/pricing
    - Extract SEO metadata and keywords
    - Generate comparison reports

16. **Automated Testing**
    - Visual regression testing with screenshots
    - End-to-end workflow validation
    - Performance monitoring

17. **Social Media Automation**
    - Auto-post to Twitter/Facebook/Instagram
    - Content scheduling and queue management
    - Engagement tracking

18. **Directory Population**
    - Auto-generate business listings
    - AI enrichment: descriptions, translations, images
    - Multi-language content creation

### ☁️ **Cloud & Storage (19-21)**

19. **Google Drive Integration**
    - Read/write files to client Google Drive
    - Folder creation and management
    - Shared drive access for collaboration

20. **Dropbox Integration**
    - File synchronization and backup
    - Team folder management
    - Asset distribution automation

21. **Cloud Asset Management**
    - Organize brand assets across storage providers
    - Version control for creative files
    - Automated backup workflows

### 🔍 **Research & Intelligence (22-25)**

22. **RSS News Ingestion**
    - Monitor automation industry news
    - Extract pain points and trends
    - Generate content ideas from news

23. **SEO Content Generation**
    - AI-generated blog posts and articles
    - Schema.org structured data creation
    - Multi-language SEO optimization

24. **Analytics & Reporting**
    - Generate performance dashboards
    - Lead metric tracking
    - Conversion funnel analysis

25. **Fact Checking & Grounding**
    - Google Search Grounding integration
    - Verify script facts before publishing
    - Source validation and citation

---

## Hardcoded Skills in Synthia's Persona

### Core Skills (Always Active)

```python
CORE_SKILLS = [
    "ugc-script-generation",
    "polly-character-design", 
    "landing-page-builder",
    "n8n-workflow-converter",
    "domain-scanner",
    "self-healing-monitor",
    "supabase-connector",
    "coolify-deployer",
    "voice-processor",
    "lead-generator",
    "web-scraper",
    "browser-automation",
    "google-drive-manager",
    "dropbox-manager",
    "rss-monitor",
    "seo-writer",
    "analytics-reporter",
    "fact-checker",
    "visual-generator",
    "video-pipeline",
]
```

### Skill: ugc-script-generation

**Purpose:** Generate "Pauli's Cartoon Truth" UGC ad scripts

**Trigger:** User requests content creation

**Process:**
1. Research current automation pain points via RSS
2. Generate script in Urban Gen Z/Millennial voice
3. Ensure cynical, direct, snappy tone
4. Output as valid JSON
5. Include character direction for Polly

**Output Format:**
```json
{
  "script": "Yo, tired of n8n crashes at 3am? Same...",
  "character": "Polly leaning cool, looking skeptical",
  "tone": "cynical-honest",
  "duration_seconds": 30,
  "hooks": ["pain_point", "relatability", "solution_tease"]
}
```

### Skill: polly-character-design

**Purpose:** Generate consistent Polly character artwork

**Trigger:** Visual asset needed

**Process:**
1. Load master prompt from `prompt.master.txt`
2. Apply scene-specific modifications
3. Generate via Hugging Face/Replicate/Stable Diffusion
4. Verify character identity (sunglasses, hooves, coat, beard)
5. Cache result for 30 days

**Identity Checklist:**
- ✅ Round dark sunglasses (always)
- ✅ Sheep (never another animal)
- ✅ Oversized bare hooves (no shoes)
- ✅ Long, worn coat
- ✅ Scruffy beard and fluffy wool
- ✅ Confident & mischievous expression

### Skill: browser-automation

**Purpose:** Web interaction and data extraction

**Trigger:** Web research or data collection needed

**Process:**
1. Create Playwright browser session
2. Navigate to target URL
3. Execute requested actions (click, type, scroll)
4. Extract data or take screenshot
5. Close session

**Capabilities:**
- Navigate to any URL
- Fill forms and submit
- Click elements
- Extract text, links, images
- Execute JavaScript
- Take screenshots (viewport or full-page)
- Scroll pages

### Skill: google-drive-manager

**Purpose:** Access and manage Google Drive files

**Trigger:** File operation requested

**Process:**
1. Authenticate with service account
2. Execute requested operation
3. Return file metadata or content

**Capabilities:**
- List files in folders
- Download files
- Upload files
- Create folders
- Delete files
- Search by name

### Skill: dropbox-manager

**Purpose:** Access and manage Dropbox files

**Trigger:** File operation requested

**Process:**
1. Authenticate with access token
2. Execute requested operation
3. Return file metadata or content

**Capabilities:**
- List files
- Download files
- Upload files
- Create folders
- Delete files

---

## Chrome DevTools Integration

### MCP Server: chrome-devtools

**Repository:** https://github.com/ChromeDevTools/chrome-devtools-mcp

**Capabilities:**
- DOM inspection and manipulation
- Network monitoring
- Performance profiling
- Console execution
- Screenshot capture
- Mobile device emulation

**Usage in Synthia:**
```python
# Example: Profile page performance
devtools = ChromeDevToolsMCP()
await devtools.navigate("https://example.com")
profile = await devtools.start_profiling()
# ... interactions ...
results = await devtools.stop_profiling()
```

### Additional Chrome DevTools Repos to Install

Based on scanning https://github.com/ChromeDevTools:

1. **chrome-devtools-mcp** - Main MCP server ✓
2. **devtools-protocol** - Protocol definitions
3. **chrome-launcher** - Launch Chrome programmatically
4. **Puppeteer** - High-level Chrome control (alternative to Playwright)

---

## Integration Architecture

```
Synthia (The Pauli Effect)
├── Core Services
│   ├── Voice (ElevenLabs - ES/EN/HI/SR)
│   ├── Media (Nano Banana, DALL-E, Runway, Pika)
│   ├── Browser (Playwright/CDP)
│   ├── Cloud (Google Drive, Dropbox)
│   └── AI (Claude, GPT-4, Ollama)
├── Skills
│   ├── Content Creation (UGC, Polly, Landing Pages)
│   ├── Automation (n8n converter, self-healing)
│   ├── Web (scraping, browser, testing)
│   └── Intelligence (research, SEO, analytics)
└── Integrations
    ├── Lemon AI (Orchestrator)
    ├── Supabase (Database)
    ├── Coolify (Deployment)
    ├── Firecrawl (Web Data)
    └── Chrome DevTools (Browser)
```

---

## Environment Variables

```bash
# Chrome DevTools
CHROME_HEADLESS=true
CHROME_EXECUTABLE=/usr/bin/google-chrome

# Google Drive
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials.json

# Dropbox
DROPBOX_ACCESS_TOKEN=your_token_here

# Firecrawl
FIRECRAWL_API_KEY=your_key_here

# Apollo
APOLLO_API_KEY=your_key_here

# RSS Feeds
RSS_FEEDS_URL=https://example.com/feeds.json
```

---

## Success Metrics

Synthia tracks these KPIs for The Pauli Effect:

1. **Content Output:** Scripts generated per day
2. **Landing Page Conversion:** % of visitors who convert
3. **Automation Uptime:** % of workflows running without failure
4. **Lead Generation:** Leads captured per day
5. **Deployment Speed:** Time from code to production
6. **Cost Efficiency:** API usage vs. output volume
7. **Quality Score:** Awwwards compliance, WCAG AA adherence

---

**Synthia v4.2** | The Pauli Effect | Autonomous AI Agency Engine
