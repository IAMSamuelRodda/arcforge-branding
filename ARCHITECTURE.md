# System Architecture

**Brand Forge** - Technical architecture, design decisions, and component specifications.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Design Philosophy](#design-philosophy)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack Rationale](#technology-stack-rationale)
6. [Scaling Considerations](#scaling-considerations)
7. [Security Architecture](#security-architecture)
8. [Integration Patterns](#integration-patterns)
9. [Future Architecture Evolution](#future-architecture-evolution)

---

## System Overview

Brand Forge is a **multi-model AI pipeline** that generates, scores, and exports brand assets with minimal human intervention.

### Core Capabilities

| Capability | Description | Target |
|------------|-------------|--------|
| **Generation** | AsyncIO-based multi-model image generation | 50+ images/hour |
| **Scoring** | 4-dimensional weighted quality assessment | ρ > 0.70 correlation |
| **Approval** | Human-in-the-loop checkpoints at 3 stages | <10 min per checkpoint |
| **Export** | Production-ready asset pipeline (4K, SVG, multi-format) | 3-5 logos/run |
| **Cost** | Budget-aware model allocation | $30-60/month |

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Stability AI │  │ Replicate    │  │   OpenAI     │  │  GitHub    │ │
│  │ (SD 3.5 API) │  │ (Flux API)   │  │ (DALL-E API) │  │  (Issues)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                 │                 │         │
└─────────┼─────────────────┼─────────────────┼─────────────────┼─────────┘
          │                 │                 │                 │
          │                 │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────────────┼─────────┐
│         │                 │                 │                 │         │
│         ▼                 ▼                 ▼                 ▼         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              AsyncIO Generation Orchestrator                      │  │
│  │  (Concurrent API calls, rate limiting, retry logic)              │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                   Quality Scoring Engine                          │  │
│  │  ┌────────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────────┐ │  │
│  │  │CLIP (30%)  │ │ Color (25%)  │ │Aesthetic   │ │Composition  │ │  │
│  │  │Similarity  │ │ Adherence    │ │Predictor   │ │Analysis     │ │  │
│  │  │            │ │              │ │(25%)       │ │(20%)        │ │  │
│  │  └────────────┘ └──────────────┘ └────────────┘ └─────────────┘ │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                SQLite Metadata Database                           │  │
│  │  (Lineage, scores, approval status, cost tracking)               │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Human Approval Interface                             │  │
│  │  ┌────────────────────┐      ┌──────────────────────────┐        │  │
│  │  │  CLI Gallery       │      │  Flask Web Dashboard     │        │  │
│  │  │  (Rich Terminal)   │ ◄──► │  (Tailwind CSS UI)       │        │  │
│  │  └────────────────────┘      └──────────────────────────┘        │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │           Production Export Pipeline                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Real-ESRGAN  │→ │    rembg     │→ │ potrace + Multi-Format │ │  │
│  │  │ (Upscaling)  │  │ (BG Removal) │  │ (SVG, PNG, PDF)        │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│                         BRAND FORGE PIPELINE                             │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Design Philosophy

### 1. Human-in-the-Loop Automation

**Principle**: Automate repetitive tasks, retain human judgment for creative decisions.

```
Human Involvement: <10 minutes per checkpoint
Machine Work: ~10-20 hours of generation, scoring, refinement

Checkpoint 1 (Concept):    Human reviews top 50/300  (5 min)
Checkpoint 2 (Direction):  Human reviews top 20/100  (3 min)
Checkpoint 3 (Final):      Human reviews top 5/30    (2 min)
```

**Why**: Balances creative control with efficiency gains. Humans excel at subjective aesthetic judgment; machines excel at parameter exploration.

### 2. Cost-Optimized Multi-Model Strategy

**Principle**: Use cheaper models for bulk exploration, expensive models for targeted refinement.

```
Stable Diffusion 3.5: 70% allocation ($0.004/img)  → Bulk exploration
Flux Schnell:         20% allocation ($0.003/img)  → Quality comparisons
DALL-E 3:             10% allocation ($0.04/img)   → Text-heavy fallback
```

**Why**: Achieves 500-1000 generations/month within $30-60 budget by allocating expensive models only where they add unique value.

### 3. Weighted Quality Scoring

**Principle**: Multi-dimensional scoring mirrors human aesthetic judgment.

```
CLIP Semantic Similarity:  30%  (Does it match the design brief?)
Brand Color Adherence:     25%  (Does it use our palette?)
Aesthetic Prediction:      25%  (Is it objectively beautiful?)
Composition Analysis:      20%  (Is it well-balanced?)
```

**Why**: Single-metric scoring (e.g., CLIP alone) misses critical brand-specific criteria. Weighted approach targets ρ > 0.70 correlation with human judgment.

### 4. Vertical Slice Architecture

**Principle**: Each component operates independently with complete functionality.

```
Prompt Engine:    Standalone template processor
Generation:       Async orchestrator with pluggable API clients
Scoring:          Independent scoring modules
Approval:         Self-contained CLI + web interfaces
Export:           Isolated upscaling/conversion pipeline
```

**Why**: Enables incremental development, parallel testing, and easy component replacement without cascading changes.

---

## Component Architecture

### 1. Prompt Generation Engine

**Location**: `automation/src/prompt_engine/`

**Responsibilities**:
- Load prompt template files (PROMPT-TEMPLATES-*.md)
- Parse DESIGN-BRIEF.md for brand specifications
- Substitute variables (colors, visual directions, typography)
- Generate prompt variations (parameter sweeps, style mixing)
- Track prompt effectiveness over time

**Key Classes**:

```python
class PromptTemplate:
    """Represents a single prompt template with placeholders."""
    def __init__(self, template_str: str, metadata: dict):
        self.template = template_str
        self.variables = self._extract_variables()

    def render(self, context: dict[str, str]) -> str:
        """Substitute variables with context values."""
        pass

class PromptEngine:
    """Main orchestrator for prompt generation."""
    def __init__(self, config: PromptConfig):
        self.templates = self._load_templates()
        self.brand_context = self._load_design_brief()

    def generate_batch(self, count: int) -> list[str]:
        """Generate batch of prompts with variations."""
        pass
```

**Design Decisions**:
- **Jinja2 templating**: Industry-standard, supports loops/conditionals
- **YAML frontmatter**: Metadata in template files (model preferences, weights)
- **Version control**: Templates are markdown files in git for easy diffing

### 2. Multi-Model Generation Pipeline

**Location**: `automation/src/generation/`

**Responsibilities**:
- Orchestrate concurrent API calls across 3 models
- Handle rate limiting, retries, errors
- Track costs per model
- Store images with lineage metadata

**Key Classes**:

```python
@dataclass
class GenerationRequest:
    """Single generation request."""
    prompt: str
    model: Literal["sd35", "flux", "dalle"]
    params: dict
    parent_id: Optional[int] = None  # For img2img refinement

class GenerationOrchestrator:
    """AsyncIO-based multi-model coordinator."""
    def __init__(self, config: GenerationConfig):
        self.clients = {
            "sd35": StableDiffusionClient(),
            "flux": FluxClient(),
            "dalle": DALLEClient()
        }

    async def generate_batch(
        self,
        requests: list[GenerationRequest]
    ) -> list[GeneratedImage]:
        """Generate images concurrently across models."""
        tasks = [self._generate_single(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _generate_single(
        self,
        req: GenerationRequest
    ) -> GeneratedImage:
        """Generate single image with retry logic."""
        client = self.clients[req.model]
        for attempt in range(3):
            try:
                return await client.generate(req.prompt, req.params)
            except RateLimitError:
                await asyncio.sleep(2 ** attempt)
            except APIError as e:
                if e.is_retryable:
                    continue
                raise
```

**Design Decisions**:
- **AsyncIO**: Enables 50+ concurrent API calls without threading overhead
- **Pluggable clients**: Each model has isolated client (easy to swap providers)
- **Exponential backoff**: Handles rate limiting gracefully
- **Cost tracking**: Every API call logged with model + cost

### 3. Quality Scoring System

**Location**: `automation/src/scoring/`

**Responsibilities**:
- Score images on 4 dimensions (CLIP, color, aesthetic, composition)
- Compute weighted composite score
- Rank and filter images by threshold

**Key Classes**:

```python
class WeightedScorer:
    """Orchestrates multi-dimensional scoring."""
    def __init__(self, config: ScoringConfig):
        self.scorers = {
            "clip": CLIPSimilarityScorer(weight=0.30),
            "color": BrandColorScorer(weight=0.25),
            "aesthetic": AestheticPredictor(weight=0.25),
            "composition": CompositionAnalyzer(weight=0.20)
        }

    def score(self, image: Image, prompt: str) -> ScoredImage:
        """Compute weighted composite score."""
        scores = {
            name: scorer.score(image, prompt)
            for name, scorer in self.scorers.items()
        }
        composite = sum(s * self.scorers[name].weight
                       for name, s in scores.items())
        return ScoredImage(image, scores, composite)
```

**Scoring Components**:

#### CLIP Semantic Similarity (30%)
- Model: OpenAI CLIP ViT-L/14
- Method: Cosine similarity between image and prompt embeddings
- Why: Best proxy for "does image match design brief intent"

#### Brand Color Adherence (25%)
- Method: K-means clustering → extract dominant colors → compute ΔE distance to brand palette
- Threshold: ΔE < 5 for 95%+ accuracy
- Why: Brand consistency is non-negotiable

#### Aesthetic Prediction (25%)
- Model: LAION Aesthetic Predictor V2
- Method: Regression score (1-10) predicting human aesthetic judgment
- Why: Catches objectively poor compositions that CLIP misses

#### Composition Analysis (20%)
- Metrics: Rule of thirds adherence, visual balance, negative space ratio
- Method: OpenCV edge detection + grid analysis
- Why: Technical quality matters for production assets

### 4. Human Approval Interface

**Location**: `automation/web/`

**Responsibilities**:
- Display scored images in gallery view
- Capture approval/rejection decisions
- Collect feedback for future refinement
- Track analytics (time per review, approval rate)

**Two Interfaces**:

```
┌─────────────────────────────────────────┐
│       CLI Gallery (Rich Terminal)       │
│  - Fast keyboard navigation (j/k/space) │
│  - ASCII art thumbnails                 │
│  - Inline score display                 │
│  - Best for: Agents, headless servers   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Flask Web Dashboard               │
│  - Responsive Tailwind CSS grid         │
│  - Full-resolution previews             │
│  - Side-by-side comparisons             │
│  - Best for: Human reviewers            │
└─────────────────────────────────────────┘
```

**Design Decisions**:
- **Dual interfaces**: CLI for automation, web for humans
- **SQLite approval state**: Persistent approval decisions, resumable sessions
- **Analytics tracking**: Time-per-review, approval rate by stage

### 5. Production Export Pipeline

**Location**: `automation/src/export/`

**Responsibilities**:
- Upscale approved images to 4K (Real-ESRGAN)
- Remove backgrounds (rembg)
- Convert to vector format (potrace)
- Export multiple formats (PNG, SVG, PDF, EPS)

**Pipeline Stages**:

```python
class ExportPipeline:
    """Production asset finalization pipeline."""
    def __init__(self, config: ExportConfig):
        self.upscaler = RealESRGANUpscaler()
        self.bg_remover = RembgProcessor()
        self.vectorizer = PotraceVectorizer()

    def process(self, image: ApprovedImage) -> ExportPackage:
        """Transform approved image to production assets."""
        # Stage 1: Upscale to 4K
        upscaled = self.upscaler.upscale(image, target_size=4096)

        # Stage 2: Remove background
        no_bg = self.bg_remover.remove_background(upscaled)

        # Stage 3: Vectorize (if quality passes threshold)
        svg = None
        if self._is_vectorizable(no_bg):
            svg = self.vectorizer.to_svg(no_bg, colors=3)

        # Stage 4: Export formats
        return ExportPackage(
            png_4k=upscaled,
            png_transparent=no_bg,
            svg=svg,
            metadata=self._generate_metadata(image)
        )
```

**Design Decisions**:
- **Real-ESRGAN**: Best open-source upscaling (beats bicubic by 20+ PSNR)
- **rembg**: U2-Net model with 95%+ accuracy on logos
- **potrace**: Industry-standard raster→vector conversion
- **Multi-color SVG**: 3-layer tracing for brand colors (not single-path)

---

## Data Flow

### Generation → Scoring → Approval → Export

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Initial Generation                                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Prompt Templates (6 files) ──┐                                          │
│  Design Brief (brand specs)  ─┤                                          │
│                                ▼                                          │
│                        Prompt Engine                                      │
│                                │                                          │
│                                ▼                                          │
│                    300 prompt variations                                  │
│                                │                                          │
│                  ┌─────────────┼─────────────┐                           │
│                  │             │             │                           │
│                  ▼             ▼             ▼                           │
│            SD 3.5 (70%)   Flux (20%)   DALL-E (10%)                      │
│                  │             │             │                           │
│                  └─────────────┼─────────────┘                           │
│                                │                                          │
│                                ▼                                          │
│                     300 generated images                                  │
│                                │                                          │
│                                ▼                                          │
│                          SQLite Insert                                    │
│                    (image_id, prompt, model, cost)                        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Quality Scoring                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  For each image:                                                          │
│    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│    │ CLIP     │   │  Color   │   │Aesthetic │   │Composit. │           │
│    │ Score    │   │  Score   │   │ Score    │   │  Score   │           │
│    │ (0-1)    │   │  (0-1)   │   │  (0-1)   │   │  (0-1)   │           │
│    └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘           │
│         │              │              │              │                   │
│         └──────────────┼──────────────┼──────────────┘                   │
│                        ▼              ▼              ▼                   │
│              Composite = 0.30*clip + 0.25*color +                        │
│                          0.25*aesthetic + 0.20*composition               │
│                        │                                                 │
│                        ▼                                                 │
│                  SQLite Update                                            │
│            (scores, composite_score, rank)                                │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Human Approval (Checkpoint 1 - Concept Selection)                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Query: SELECT * FROM images                                              │
│         WHERE stage = 'initial'                                           │
│         ORDER BY composite_score DESC                                     │
│         LIMIT 50                                                          │
│                        │                                                 │
│                        ▼                                                 │
│              Web Dashboard Display                                        │
│         (Grid view, score overlays, filter by model)                     │
│                        │                                                 │
│                        ▼                                                 │
│          Human selects 10 images (~5 min)                                │
│                        │                                                 │
│                        ▼                                                 │
│                  SQLite Update                                            │
│          (approval_status = 'approved_concept')                           │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Iterative Refinement (img2img)                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Approved images (10) ──┐                                                │
│                         ▼                                                │
│                Parameter Exploration                                      │
│        (Strength: 0.3, 0.5, 0.7 × Seed variations)                       │
│                         │                                                │
│                         ▼                                                │
│             100 refined images (10 × 10 variations)                       │
│                         │                                                │
│                         ▼                                                │
│                   Re-score all                                            │
│                         │                                                │
│                         ▼                                                │
│    Checkpoint 2: Human reviews top 20 (~3 min)                           │
│    Approves 5 for final refinement                                       │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 5: Final Refinement & Selection                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Approved images (5) ──┐                                                 │
│                        ▼                                                 │
│            High-quality refinement                                        │
│      (Strength: 0.2, CFG: 8.0, Steps: 50)                                │
│                        │                                                 │
│                        ▼                                                 │
│             30 final candidates (5 × 6 variations)                        │
│                        │                                                 │
│                        ▼                                                 │
│                   Re-score all                                            │
│                        │                                                 │
│                        ▼                                                 │
│    Checkpoint 3: Human selects 3-5 for production (~2 min)               │
│                        │                                                 │
│                        ▼                                                 │
│              SQLite Update                                                │
│        (approval_status = 'production_approved')                          │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Stage 6: Production Export                                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Production-approved images (3-5) ──┐                                    │
│                                     ▼                                    │
│                            Real-ESRGAN Upscale                            │
│                         (1024px → 4096px 4K)                              │
│                                     │                                    │
│                                     ▼                                    │
│                          rembg Background Removal                         │
│                       (U2-Net transparent PNG)                            │
│                                     │                                    │
│                                     ▼                                    │
│                          potrace Vectorization                            │
│                       (3-color SVG tracing)                               │
│                                     │                                    │
│                                     ▼                                    │
│                          Multi-Format Export                              │
│              ┌──────────────┬──────────────┬──────────────┐             │
│              ▼              ▼              ▼              ▼             │
│         PNG 4K       PNG Transparent    SVG Vector      PDF Print        │
│                                                                           │
│                              ▼                                            │
│                   assets/approved/                                        │
│               {timestamp}_{image_id}/                                     │
│                 ├── logo_4k.png                                           │
│                 ├── logo_transparent.png                                  │
│                 ├── logo_vector.svg                                       │
│                 ├── logo_print.pdf                                        │
│                 └── metadata.json                                         │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Rationale

### Core Language: Python 3.11+

**Why Python**:
- **AI/ML ecosystem**: CLIP, scikit-learn, OpenCV, PIL all Python-native
- **AsyncIO**: Native async/await for concurrent API calls
- **Rapid development**: Rich libraries reduce boilerplate

**Why 3.11+**:
- **Performance**: 10-25% faster than 3.10 (PEP 659 specializing interpreter)
- **Type hints**: Improved error messages for Optional, Union types
- **Exception groups**: Better async error handling

### Package Manager: uv

**Why uv** (not pip):
- **Speed**: 10-100x faster than pip (Rust-based resolver)
- **Compatibility**: Drop-in replacement, same CLI
- **Reliability**: Deterministic resolution (like poetry but faster)

### Database: SQLite

**Why SQLite** (not PostgreSQL):
- **Simplicity**: Zero-configuration, single file
- **Performance**: 50,000+ writes/sec with WAL mode
- **Scale**: Handles 500K images + metadata easily
- **Why not Postgres**: Overkill for single-user system, adds deployment complexity

### Web Framework: Flask

**Why Flask** (not FastAPI/Django):
- **Simplicity**: Minimal boilerplate for approval UI
- **Ecosystem**: Huge plugin library (Flask-CORS, Flask-SocketIO)
- **Templates**: Jinja2 templating matches prompt engine
- **Why not FastAPI**: Don't need OpenAPI docs for internal tool
- **Why not Django**: Too heavy for 3-page approval interface

### AsyncIO (not Threading)

**Why AsyncIO**:
- **Scalability**: 1000+ concurrent connections without thread overhead
- **Composability**: async/await composes better than callbacks
- **Library support**: aiohttp, asyncpg, aiobotocore all async-native

**When NOT to use AsyncIO**:
- CPU-bound tasks (use multiprocessing for image processing)
- Synchronous libraries (Real-ESRGAN, rembg run in thread pool)

---

## Scaling Considerations

### Current Architecture: Single-User, Local Execution

**Designed for**:
- 1 user generating 500-1000 images/month
- Local Python execution (laptop or workstation)
- SQLite database (<500MB for 10K images)

**Bottlenecks at Scale**:

| Component | Current Limit | Bottleneck |
|-----------|---------------|------------|
| Generation | 50 images/hour | API rate limits |
| Scoring | 200 images/hour | CPU (CLIP inference) |
| Storage | 500K images | SQLite file size (250GB) |
| Web UI | 1 concurrent user | No authentication |

### Scaling to 10 Users (5K images/month)

**Changes needed**:
1. **Database**: Migrate to PostgreSQL for concurrent writes
2. **Authentication**: Add Flask-Login for multi-user approval
3. **File storage**: S3/Cloudflare R2 for images (not local disk)
4. **Queue system**: Redis + Celery for background generation tasks

**Estimated effort**: 2-3 weeks

### Scaling to 100 Users (50K images/month)

**Changes needed**:
1. **Containerization**: Docker + Kubernetes for horizontal scaling
2. **Load balancing**: NGINX for web UI, round-robin API clients
3. **Caching**: Redis for CLIP embeddings, brand color calculations
4. **Observability**: Prometheus + Grafana for metrics

**Estimated effort**: 1-2 months

---

## Security Architecture

### Current Threat Model

**Assets to protect**:
1. API keys (OpenAI, Stability AI, Replicate)
2. Generated images (pre-approval, may contain bad outputs)
3. Approved images (production assets, competitive advantage)

**Threats**:
- **Key leakage**: Accidental commit to git
- **Local file access**: Unauthorized access to results/data directories
- **Cost abuse**: API key stolen → unlimited generation charges

### Security Controls

#### 1. Secret Management

```yaml
# automation/config/config.yaml (gitignored)
models:
  stable_diffusion:
    api_key: "${SD_API_KEY}"  # Environment variable required
  openai:
    api_key: "${OPENAI_API_KEY}"

# Never hardcode keys in code
```

**Why**: Environment variables prevent accidental git commits. If compromised, rotate keys without code changes.

#### 2. File Permissions

```bash
# Restrict database access
chmod 600 automation/data/*.db

# Restrict config access
chmod 600 automation/config/config.yaml

# Make results directory read-only after generation
chmod -R 444 automation/results/approved/
```

#### 3. Cost Controls

```python
class BudgetEnforcer:
    """Prevent runaway API costs."""
    def __init__(self, monthly_limit: float):
        self.limit = monthly_limit

    def check_budget(self) -> bool:
        """Verify budget not exceeded."""
        current_spend = self._get_monthly_spend()
        if current_spend >= self.limit * 0.90:
            logging.warning(f"90% budget consumed: ${current_spend:.2f}")
        if current_spend >= self.limit:
            raise BudgetExceededError(f"Monthly limit ${self.limit} reached")
        return True
```

**Why**: Prevents accidental $1000+ bills from infinite loops or compromised keys.

---

## Integration Patterns

### 1. API Client Pattern (Generation)

```python
class APIClient(ABC):
    """Abstract base for all generation API clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        params: dict
    ) -> GeneratedImage:
        """Generate single image."""
        pass

    async def _retry_with_backoff(
        self,
        fn: Callable,
        max_retries: int = 3
    ):
        """Exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                return await fn()
            except RateLimitError:
                wait = 2 ** attempt
                logging.warning(f"Rate limited, waiting {wait}s")
                await asyncio.sleep(wait)
        raise MaxRetriesExceeded()

class StableDiffusionClient(APIClient):
    """Stability AI SD 3.5 client."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def generate(self, prompt: str, params: dict):
        return await self._retry_with_backoff(
            lambda: self._generate_impl(prompt, params)
        )
```

**Pattern**: Abstract base class + concrete implementations for each model. Shared retry logic, isolated API differences.

### 2. Scorer Registry Pattern (Quality Scoring)

```python
class ScorerRegistry:
    """Registry of available scoring modules."""
    _scorers: dict[str, Type[Scorer]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register scorer."""
        def wrapper(scorer_cls):
            cls._scorers[name] = scorer_cls
            return scorer_cls
        return wrapper

    @classmethod
    def create(cls, name: str, **kwargs) -> Scorer:
        """Factory method to instantiate scorer."""
        return cls._scorers[name](**kwargs)

@ScorerRegistry.register("clip")
class CLIPSimilarityScorer(Scorer):
    def score(self, image: Image, prompt: str) -> float:
        # Implementation
        pass
```

**Pattern**: Registry + factory for dynamic scorer instantiation. Add new scorers without modifying orchestrator.

### 3. Pipeline Pattern (Export)

```python
class PipelineStage(ABC):
    """Abstract pipeline stage."""
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass

class ExportPipeline:
    """Composable export pipeline."""
    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages

    def execute(self, image: Image) -> ExportPackage:
        """Execute all stages sequentially."""
        result = image
        for stage in self.stages:
            result = stage.process(result)
        return result

# Usage
pipeline = ExportPipeline([
    UpscaleStage(),
    BackgroundRemovalStage(),
    VectorizationStage(),
    MultiFormatExportStage()
])
```

**Pattern**: Chain of responsibility for sequential processing. Easy to add/remove/reorder stages.

---

## Future Architecture Evolution

### Phase 1 (Current): Local Single-User
- Python CLI + Flask web UI
- SQLite database
- Local file storage
- Manual execution

### Phase 2: Multi-User Cloud Deployment (6 months)
- Containerization (Docker)
- PostgreSQL database
- S3 file storage
- Authentication + authorization
- Background job queue (Celery)

### Phase 3: Enterprise SaaS (12 months)
- Kubernetes orchestration
- Multi-tenancy (org isolation)
- Stripe billing integration
- Admin dashboard
- Public API (REST + GraphQL)

### Phase 4: AI Agent Marketplace (18 months)
- Plugin architecture for custom scorers
- User-contributed prompt templates
- Model fine-tuning on approved images
- Automated A/B testing of prompts

---

## Appendix: Technology Alternatives Considered

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Language | Python 3.11+ | TypeScript | AI/ML ecosystem |
| Package Manager | uv | pip, poetry | Speed (10-100x faster) |
| Database | SQLite | PostgreSQL | Simplicity for single-user |
| Web Framework | Flask | FastAPI, Django | Right size for approval UI |
| Async Runtime | AsyncIO | Threading | Better for I/O-bound tasks |
| Image Library | Pillow | OpenCV | Simpler API, good enough |
| Upscaling | Real-ESRGAN | ESRGAN, SwinIR | Best quality/speed balance |
| Vectorization | potrace | Inkscape, Illustrator | Scriptable, open-source |
| Background Removal | rembg | Photoshop API | Cost-effective, good quality |

---

**Last Updated**: November 10, 2025
