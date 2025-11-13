# Stable Diffusion API Deployment Decision

**Date**: 2025-11-13
**Status**: Research Phase
**Decision Owner**: Development Team
**Context**: Feature #2.2 - Stable Diffusion API Integration (Epic #11)

---

## Executive Summary

**Recommendation for Development Mode**: **Replicate API with Flux Schnell**

**Rationale**:
- **10x cheaper** than Stable Diffusion ($0.003 vs $0.03+ per generation)
- **Fast iteration** for development (1-2 sec generation)
- **No infrastructure setup** required
- **Easy migration path** to self-hosted or other APIs for production
- **Budget-friendly**: 500 images = $1.50 (vs $15+ with SD)

---

## Requirements Analysis

From `specs/BLUEPRINT-DESIGNFORGE.yaml`:

**Deliverables**:
1. API client for image generation
2. Async batch handling (50+ concurrent requests)
3. Error handling (timeouts, rate limits, availability)
4. Cost tracking with budget alerts ($30-60/month)

**Success Criteria** (Milestone 1):
- Generate 50+ images from design brief
- Support quality scoring and approval pipeline
- Track complete lineage from prompt to image

**Budget Constraint**: $30-60/month total project budget

---

## Option 1: Replicate API with Flux Schnell ⭐ RECOMMENDED

### Overview
[Replicate](https://replicate.com) is a cloud platform for running ML models with pay-per-use pricing. Flux Schnell is a fast, high-quality image generation model.

### Cost Analysis

**Pricing**: $0.003 per image (Flux Schnell)

| Volume | Cost | Budget % |
|--------|------|----------|
| 500 images | $1.50 | 2.5% |
| 1,000 images | $3.00 | 5% |
| 5,000 images | $15.00 | 25% |
| 10,000 images | $30.00 | 50% |

**Development Budget Impact**:
- Testing phase (500 images): $1.50
- Initial dataset (1,000 images): $3.00
- **Leaves $27-57 for other APIs** (scoring, refinement, etc.)

### Performance

- **Generation Speed**: 1-2 seconds per image
- **Quality**: High (Flux is competitive with SD 3.5)
- **Concurrency**: Replicate handles batch requests (50+ concurrent)
- **Rate Limits**: 100 requests/second on paid plans

### Technical Requirements

```python
# Example implementation
import replicate

async def generate_image(prompt: str) -> str:
    output = await replicate.async_run(
        "black-forest-labs/flux-schnell",
        input={"prompt": prompt}
    )
    return output[0]  # Image URL
```

**Dependencies**:
- `replicate` Python SDK
- API token (requires account signup)
- No GPU infrastructure

### Pros ✅
- **Lowest cost** for development ($0.003/image)
- **No infrastructure setup** (cloud-hosted)
- **Fast iteration** (1-2 sec generation)
- **Simple API** (single SDK, well-documented)
- **Scalable** (handles batch requests)
- **Budget-friendly** (10,000 images = $30)

### Cons ❌
- **Requires internet** (no offline generation)
- **Vendor dependency** (locked to Replicate)
- **API rate limits** (though generous for our use case)
- **Slight model differences** (Flux vs SD - need to verify quality matches requirements)

### Migration Path

If we need to switch later:
1. **To Stability AI**: Change API endpoint, adjust parameters
2. **To self-hosted**: Use same async batch architecture
3. **To other providers**: Replicate also hosts SD 3.5 ($0.035/image) for easy testing

---

## Option 2: Stability AI API (Stable Diffusion 3.5)

### Overview
Official Stability AI API for Stable Diffusion 3.5.

### Cost Analysis

**Pricing**: $0.03-0.04 per image (SD 3.5 Medium)

| Volume | Cost | Budget % |
|--------|------|----------|
| 500 images | $15-20 | 25-33% |
| 1,000 images | $30-40 | 50-67% |
| 5,000 images | $150-200 | 250-333% ⚠️ |

**Development Budget Impact**:
- Testing phase (500 images): $15-20 (uses 25-33% of budget)
- Initial dataset (1,000 images): $30-40 (**exceeds budget**)

### Performance

- **Generation Speed**: 3-5 seconds per image
- **Quality**: High (official SD 3.5 model)
- **Concurrency**: API supports batch requests
- **Rate Limits**: Tier-dependent (basic tier: 10 req/sec)

### Technical Requirements

```python
import stability_sdk

async def generate_image(prompt: str) -> bytes:
    api = stability_sdk.client.StabilityInference(key=os.environ["STABILITY_KEY"])
    response = await api.generate_async(prompt=prompt)
    return response.artifacts[0].binary
```

**Dependencies**:
- `stability-sdk` Python SDK
- API key (requires paid account)
- Credit card for billing

### Pros ✅
- **Official SD model** (guaranteed compatibility)
- **High quality** (SD 3.5 is state-of-the-art)
- **Well-documented** API
- **No infrastructure management**

### Cons ❌
- **10x more expensive** than Flux ($0.03 vs $0.003)
- **Budget constraints**: 500 images uses 25-33% of total budget
- **Requires paid account** (credit card)
- **Still vendor-dependent**

---

## Option 3: Self-Hosted Stable Diffusion

### Overview
Run SD 3.5 locally on GPU hardware.

### Cost Analysis

**Initial Setup**:
- GPU rental (AWS g4dn.xlarge): $0.526/hour = $378/month ⚠️
- GPU rental (Lambda Labs): $0.50/hour = $360/month ⚠️
- **Local GPU**: $0/month (if available)

**Per-Image Cost**: $0 (after setup)

| Volume | Cost | Notes |
|--------|------|-------|
| Any volume | $0 | Unlimited generations |

**Development Budget Impact**:
- **With cloud GPU**: Exceeds budget ($360-378/month)
- **With local GPU**: Free (but requires hardware)

### Performance

- **Generation Speed**: 3-8 seconds per image (GPU-dependent)
- **Quality**: High (full SD 3.5 model)
- **Concurrency**: Limited by GPU memory
- **Rate Limits**: None (local)

### Technical Requirements

**Hardware**:
- NVIDIA GPU with 8GB+ VRAM (RTX 3060, A10, etc.)
- 16GB+ system RAM
- 50GB+ disk space for models

**Software**:
```bash
# Installation
pip install diffusers transformers torch
huggingface-cli download stabilityai/stable-diffusion-3.5-large

# Usage
from diffusers import StableDiffusion3Pipeline
pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/sd-3.5-large")
image = pipe(prompt="...").images[0]
```

**Dependencies**:
- PyTorch with CUDA
- Hugging Face account (free)
- Model weights (20-40GB download)

### Pros ✅
- **Zero per-image cost** (after setup)
- **No rate limits** (local control)
- **Offline generation** (no internet required)
- **Full model control** (custom fine-tuning possible)
- **No vendor lock-in**

### Cons ❌
- **High initial setup complexity** (GPU drivers, CUDA, model download)
- **Cloud GPU costs exceed budget** ($360-378/month)
- **Local GPU required** (not available on all dev machines)
- **Maintenance burden** (model updates, CUDA compatibility)
- **Slower generation** on CPU (30+ seconds per image)
- **Not cost-effective for development** (unless GPU already available)

---

## Option 4: Mock API (Development Only)

### Overview
Fake API client that returns placeholder images for testing workflows without costs.

### Cost Analysis

**Cost**: $0 (no real generation)

### Performance

- **Generation Speed**: Instant (<0.1 sec)
- **Quality**: N/A (placeholder images)
- **Concurrency**: Unlimited
- **Rate Limits**: None

### Technical Requirements

```python
class MockSDClient:
    async def generate(self, prompt: str) -> bytes:
        # Return placeholder image
        return self._create_placeholder_image(prompt)

    def _create_placeholder_image(self, prompt: str) -> bytes:
        # Generate 512x512 colored rectangle with prompt text
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (512, 512), color=(100, 100, 100))
        # Add text overlay...
        return img.tobytes()
```

### Pros ✅
- **Zero cost** (no API calls)
- **Instant generation** (testing workflows)
- **No API keys required**
- **Offline development**

### Cons ❌
- **No real images** (can't test quality scoring)
- **Development only** (not production-ready)
- **Limited testing** (can't validate prompt effectiveness)

---

## Decision Matrix

| Criteria | Replicate (Flux) | Stability AI | Self-Hosted | Mock API |
|----------|-----------------|--------------|-------------|----------|
| **Cost (500 images)** | $1.50 ⭐ | $15-20 | $0 or $378/mo | $0 |
| **Cost (1,000 images)** | $3.00 ⭐ | $30-40 | $0 or $378/mo | $0 |
| **Setup Complexity** | Low ⭐ | Low | High ❌ | Low |
| **Generation Speed** | 1-2 sec ⭐ | 3-5 sec | 3-8 sec | <0.1 sec |
| **Quality** | High ⭐ | High ⭐ | High | N/A ❌ |
| **Budget Fit ($30-60)** | Yes ⭐ | Marginal | No ❌ | Yes |
| **Maintenance** | None ⭐ | None | High ❌ | None |
| **Production Viability** | Yes ⭐ | Yes | Yes | No ❌ |
| **Offline Support** | No | No | Yes | Yes |

**Score**:
- **Replicate (Flux)**: 8/8 ⭐⭐⭐
- **Stability AI**: 5/8
- **Self-Hosted**: 4/8 (without local GPU: 2/8)
- **Mock API**: 5/8 (dev only)

---

## Recommendation: Two-Phase Approach

### Phase 1: Development (Current) - Replicate API with Flux

**Use for**:
- Initial testing (500 images: $1.50)
- Prompt engine validation
- Quality scoring system development
- Approval workflow testing

**Benefits**:
- **Stays under budget** ($3 for 1,000 images)
- **Fast iteration** (1-2 sec generation)
- **Real image quality** (can test scoring)
- **Minimal setup** (minutes, not hours)

**Implementation**:
```python
# src/generation/sd_client.py
from replicate import AsyncClient

class StableDiffusionClient:
    def __init__(self, api_token: str):
        self.client = AsyncClient(api_token=api_token)
        self.model = "black-forest-labs/flux-schnell"

    async def generate(self, prompt: str, **params) -> bytes:
        output = await self.client.async_run(
            self.model,
            input={"prompt": prompt, **params}
        )
        # Download image from URL
        return await self._download_image(output[0])
```

### Phase 2: Production (Future) - Evaluate Based on Volume

**If volume < 5,000 images/month**: Continue with Replicate Flux ($15/month)
**If volume > 5,000 images/month**: Consider self-hosted or explore Stability AI pricing
**If quality gap identified**: Test Replicate's SD 3.5 ($0.035/image) or migrate to Stability AI

---

## Implementation Plan

### Step 1: Setup Replicate Account
```bash
# Install SDK
uv pip install replicate

# Get API token
# Visit: https://replicate.com/account/api-tokens
export REPLICATE_API_TOKEN="r8_..."
```

### Step 2: Implement API Client
- Create `src/generation/sd_client.py`
- Add async `generate()` method
- Implement batch queue for 50+ concurrent requests
- Add progress tracking with `rich` library

### Step 3: Add Error Handling
- Retry logic with exponential backoff
- Rate limit detection and backoff
- Timeout handling (10-second default)

### Step 4: Cost Tracking
- Track generations per session/month
- Calculate cumulative costs ($0.003 per image)
- Alert when approaching $30-60 threshold
- Export cost reports to `results/cost-tracking.json`

### Step 5: Testing
- Unit tests with mock client
- Integration tests with Replicate API (limit to 5 generations)
- Validate async batch handling
- Verify cost tracking accuracy

---

## Risk Assessment

### Risk 1: Flux Quality Doesn't Match Requirements
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Test 50 images with scoring system first
- Compare with SD 3.5 samples
- Replicate also hosts SD 3.5 ($0.035) for easy migration

### Risk 2: API Rate Limits
**Probability**: Low
**Impact**: Low
**Mitigation**:
- Replicate allows 100 req/sec on paid plans
- Implement rate limit backoff
- Batch queue with configurable concurrency

### Risk 3: Budget Overrun
**Probability**: Very Low
**Impact**: Medium
**Mitigation**:
- Built-in cost tracking with alerts
- Manual approval gates (can't exceed budget without user action)
- Cost estimate before batch generation: "Generate 500 images will cost $1.50. Continue? [y/N]"

---

## Alternatives Considered

### Hugging Face Inference API
- **Cost**: $0.06 per image (SD 2.1)
- **Quality**: Lower than Flux/SD 3.5
- **Verdict**: More expensive than Replicate Flux, lower quality

### RunPod Serverless
- **Cost**: $0.0002/sec (~$0.004-0.008 per image)
- **Setup**: Complex (requires custom Docker container)
- **Verdict**: Similar cost to Replicate, much higher setup complexity

### Local CPU Generation
- **Cost**: $0
- **Performance**: 30-60 seconds per image ❌
- **Verdict**: Too slow for development iteration

---

## Conclusion

**Decision**: Use **Replicate API with Flux Schnell** for Feature #2.2 implementation.

**Cost Impact**:
- Development testing (500 images): $1.50 (2.5% of budget)
- Initial dataset (1,000 images): $3.00 (5% of budget)
- **Leaves $27-57 for other features** (scoring APIs, refinement, etc.)

**Timeline**:
- API client implementation: 2 days
- Error handling & cost tracking: 0.5 days
- Testing & validation: 0.5 days
- **Total**: 3 days (within 4-day estimate)

**Next Steps**:
1. Create Replicate account and get API token
2. Implement `StableDiffusionClient` with Flux Schnell
3. Add async batch queue and progress tracking
4. Implement cost tracking with budget alerts
5. Write unit and integration tests
6. Validate with 50-100 test generations ($0.15-0.30)

---

**Approved**: Pending review
**Implementation Start**: 2025-11-13
