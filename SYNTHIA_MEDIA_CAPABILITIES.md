# 🎨 Synthia Media Generation Capabilities - The Pauli Effect

## Overview

Synthia now has access to **top-tier image and video generators** for creating stunning visuals for landing pages, ads, social media, and creative projects.

## Image Generation (4 Providers)

### 1. Nano Banana (nanobanana.ai)
- **Best For:** Artistic, creative, stylized images
- **Strengths:** Unique artistic styles, creative interpretations
- **Use Cases:** Brand illustrations, artistic assets, creative campaigns

### 2. DALL-E 3 (OpenAI)
- **Best For:** Detailed, accurate, photorealistic images
- **Strengths:** Text accuracy, detailed scenes, reliable outputs
- **Use Cases:** Product photos, realistic scenes, precise visuals

### 3. Stable Diffusion XL (Stability AI)
- **Best For:** Customization, control, local generation
- **Strengths:** Highly configurable, open-source, fast
- **Use Cases:** Custom styles, batch generation, fine-tuned outputs

### 4. Midjourney
- **Best For:** High-quality artistic images
- **Strengths:** Beautiful compositions, artistic flair
- **Use Cases:** Premium brand assets, artistic campaigns

## Video Generation (2 Providers)

### 1. RunwayML Gen-2
- **Best For:** Industry-leading AI video generation
- **Strengths:** High quality, motion consistency, professional results
- **Use Cases:** Brand videos, product showcases, cinematic content
- **Duration:** Up to 16 seconds

### 2. Pika Labs
- **Best For:** Fast, creative video generation
- **Strengths:** Quick generation, creative effects, ease of use
- **Use Cases:** Social media videos, quick prototypes, creative experiments
- **Duration:** Up to 3 seconds

## Usage Examples

### Generate Image
```python
from services import get_media_service, ImageProvider

media = get_media_service()

# Nano Banana - Artistic
image = await media.generate_image(
    prompt="A futuristic coffee shop in Mexico City, neon lights, cyberpunk style",
    provider=ImageProvider.NANO_BANANA,
    style="artistic"
)

# DALL-E 3 - Photorealistic
image = await media.generate_image(
    prompt="Professional product photo of a minimalist watch on marble surface",
    provider=ImageProvider.DALLE,
    quality="hd"
)

# Stable Diffusion - Custom
image = await media.generate_image(
    prompt="Abstract geometric pattern, brand colors #D63384 and #006847",
    provider=ImageProvider.STABLE_DIFFUSION,
    steps=50
)
```

### Generate Video
```python
from services import get_media_service, VideoProvider

media = get_media_service()

# RunwayML - Cinematic
video = await media.generate_video(
    prompt="Cinematic drone shot revealing a modern brand logo at sunset",
    provider=VideoProvider.RUNWAY_ML,
    duration=4,
    motion_scale=1.2
)

# Pika Labs - Quick
video = await media.generate_video(
    prompt="Animated logo reveal with particle effects",
    provider=VideoProvider.PIKA_LABS,
    duration=3
)

# Image to Video
video = await media.generate_video(
    prompt="Gentle camera movement, cinematic lighting",
    image_url="https://example.com/image.png",
    provider=VideoProvider.RUNWAY_ML
)
```

## API Configuration

Add these to your `.env` file:

```bash
# Image Generation
NANO_BANANA_API_KEY=your_nanobanana_key_here
MIDJOURNEY_API_KEY=your_midjourney_key_here
STABILITY_API_KEY=your_stability_key_here

# Video Generation
RUNWAY_API_KEY=your_runway_key_here
PIKA_API_KEY=your_pika_key_here
```

## Integration with Skills

Synthia's media generation integrates with her existing skills:

### Marketing Campaign
```
User: "Create a social media campaign for our new product"

Synthia:
1. marketing-growth-engine → Campaign strategy
2. generate_image (DALL-E) → Product hero image
3. generate_video (Runway) → Product demo video
4. algo-art-synthia → Supporting graphics
5. Deploy to social platforms
```

### Landing Page
```
User: "Build a landing page for Mexico City coffee shop"

Synthia:
1. ui-ux-design-master → Page design
2. generate_image (Nano Banana) → Hero illustration
3. web-artifacts-builder-plus → Build React components
4. deployment-devops-orchestrator → Deploy to Vercel
```

## File Structure

```
backend/
├── services/
│   ├── __init__.py
│   ├── voice.py                    # Voice (ES/EN/HI/SR)
│   └── media_generation.py         # Image & Video generation
│       ├── Nano Banana
│       ├── DALL-E 3
│       ├── Stable Diffusion
│       ├── Midjourney (ready)
│       ├── RunwayML
│       └── Pika Labs
```

## Quality Standards

All generated media follows The Pauli Effect quality standards:
- ✅ High resolution (1024x1024 minimum)
- ✅ Brand-appropriate content
- ✅ Multiple format support (PNG, JPG, MP4)
- ✅ Consistent with design system

---

**Synthia v4.2** | The Pauli Effect | AI-Powered Media Generation
