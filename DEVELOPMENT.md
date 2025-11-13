# Development Guide

**Brand Forge** - Development environment setup, testing strategy, and contribution guidelines.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Project Conventions](#project-conventions)
5. [Testing Strategy](#testing-strategy)
6. [Pre-Commit Checklist](#pre-commit-checklist)
7. [Debugging Guide](#debugging-guide)
8. [Performance Optimization](#performance-optimization)

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.11 or higher
- **uv**: Fast Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git**: Version control
- **GitHub CLI**: `gh` with `project` and `read:project` scopes
- **Optional**: Docker (for containerized testing)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/IAMSamuelRodda/brand-forge.git
cd brand-forge

# Create virtual environment
python3 -m venv ./.venv
source ./.venv/bin/activate  # On Windows: automation\.venv\Scripts\activate

# Verify uv is installed
uv --version  # Should show version 0.1.0+

# Install dependencies (when requirements.txt is available)
uv pip install -r ./requirements.txt

# Install development dependencies
uv pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Verify installation
python -c "import sys; print(f'Python {sys.version}')"
```

### Configuration Setup

```bash
# Copy example configuration
cp ./config/config.example.yaml ./config/config.yaml

# Edit configuration with your API keys
nano ./config/config.yaml  # or vim, code, etc.
```

**Required API Keys**:
- Stable Diffusion API key (Stability AI or self-hosted)
- Flux API key (Replicate or BFL)
- OpenAI API key (for DALL-E 3)

### GitHub CLI Setup

```bash
# Check authentication
gh auth status

# Add project management scopes if missing
gh auth refresh -h github.com -s project,read:project

# Verify project access
gh project view 6 --owner IAMSamuelRodda
```

---

## Project Architecture

### Directory Structure

```
./
├── config/
│   ├── config.yaml              # Runtime configuration (gitignored)
│   └── config.example.yaml      # Template with defaults
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── prompt_engine/
│   │   ├── __init__.py
│   │   ├── template_loader.py   # Load PROMPT-TEMPLATES-*.md
│   │   └── variable_subst.py    # Brand palette substitution
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # AsyncIO multi-model coordinator
│   │   ├── stable_diffusion.py  # SD 3.5 API client
│   │   ├── flux_client.py       # Flux Schnell client
│   │   └── dalle_client.py      # DALL-E 3 client
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── scorer.py            # Weighted scoring orchestrator
│   │   ├── clip_similarity.py   # Semantic similarity (30%)
│   │   ├── color_adherence.py   # Brand color checker (25%)
│   │   ├── aesthetic_pred.py    # Aesthetic predictor (25%)
│   │   └── composition.py       # Composition analyzer (20%)
│   ├── refinement/
│   │   ├── __init__.py
│   │   ├── img2img.py           # Iterative refinement
│   │   └── param_explore.py     # Parameter space exploration
│   ├── export/
│   │   ├── __init__.py
│   │   ├── upscaler.py          # Real-ESRGAN upscaling
│   │   ├── bg_removal.py        # rembg background removal
│   │   └── vectorizer.py        # potrace SVG conversion
│   └── db/
│       ├── __init__.py
│       ├── models.py            # SQLAlchemy models
│       └── queries.py           # Database operations
├── web/
│   ├── app.py                   # Flask/Streamlit entry
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS, assets
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── results/                     # Generated images (gitignored)
├── data/                        # SQLite DB (gitignored)
└── logs/                        # Application logs (gitignored)
```

### Component Dependencies

```
┌──────────────────────────────────────────────────────────┐
│                      main.py                             │
│              (Orchestration Entry Point)                 │
└────────────────┬─────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────┐
    │            │            │              │
    ▼            ▼            ▼              ▼
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│ Prompt │  │ Generate │  │ Scoring │  │  Export  │
│ Engine │→ │ Pipeline │→ │ System  │→ │ Pipeline │
└────────┘  └──────────┘  └─────────┘  └──────────┘
    │            │            │              │
    ▼            ▼            ▼              ▼
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│ Design │  │   APIs   │  │  CLIP   │  │Real-ESRG│
│ Briefs │  │ (SD/Flux)│  │  Color  │  │  rembg  │
└────────┘  └──────────┘  └─────────┘  └──────────┘
```

---

## Code Style Guidelines

### Python Style

Follow **PEP 8** with these additions:

```python
# Line length: 100 characters (not 79)
# Use type hints for all functions
def generate_prompt(template: str, palette: dict[str, str]) -> str:
    """
    Generate prompt from template with brand palette substitution.

    Args:
        template: Prompt template with {{variable}} placeholders
        palette: Brand color palette (name -> hex)

    Returns:
        Processed prompt string with variables substituted
    """
    pass

# Use dataclasses for configuration
from dataclasses import dataclass

@dataclass
class ModelConfig:
    api_key: str
    allocation: float
    enabled: bool = True

# Use async/await for I/O operations
async def generate_batch(prompts: list[str]) -> list[Image]:
    """Generate images concurrently across multiple models."""
    tasks = [generate_single(p) for p in prompts]
    return await asyncio.gather(*tasks)

# Use pathlib for file operations (not os.path)
from pathlib import Path

results_dir = Path("./results")
results_dir.mkdir(parents=True, exist_ok=True)
```

### Code Formatting

```bash
# Format code with Black (100 char line length)
black --line-length 100 ./src/

# Lint with Ruff (faster than flake8 + pylint)
ruff check ./src/

# Type check with mypy
mypy ./src/
```

### Import Order

```python
# Standard library
import asyncio
import logging
from pathlib import Path

# Third-party
import numpy as np
import torch
from PIL import Image

# Local application
from automation.src.generation import StableDiffusionClient
from automation.src.scoring import WeightedScorer
```

---

## Project Conventions

### Naming Conventions

- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase` (e.g., `ModelKnowledgeAdapter`, `StableDiffusionClient`)
- **Functions**: `snake_case` (e.g., `generate_variations`, `calculate_score`)
- **Config files**: `kebab-case.yaml` (e.g., `brand-criteria.yaml`, `scoring-weights.yaml`)
- **Database tables**: `snake_case` (e.g., `generations`, `prompt_effectiveness`)
- **Feature branches**: `feature/epic-N-description` or `feature/issue-N-description`

### Session Organization

- **Path pattern**: `results/{session_id}/{stage}/`
- **Stages**:
  - `stage_1_concept` - Initial generation (300+ images)
  - `stage_2_refinement` - img2img improvements
  - `stage_3_production` - Final exports
- **Retention**: 30 days (automated cleanup)
- **Image naming**: `{image_id}.png` (UUID for generated), `{brand}-logo-{direction}-{variant}.{ext}` for exports

### Multi-Model Strategy

**Budget**: $30-60/month for 500-1000 generations

**Model Allocation**:
- **Stable Diffusion 3.5**: 70% ($0.004/img) - Bulk generation
- **Flux Schnell**: 20% ($0.003/img) - Quality comparisons
- **DALL-E 3**: 10% ($0.04/img) - Text-heavy fallback

**Cost Tracking**: Real-time monitoring with alerts at 50%, 75%, 90% of budget.

### Quality Thresholds

- **Brand color accuracy**: 95%+ (using Delta E CIE 2000)
- **Scoring correlation**: Spearman's ρ > 0.7 vs human judgment
- **Scoring weights**:
  - CLIP semantic similarity: 30%
  - Brand color adherence: 25%
  - Aesthetic quality: 25%
  - Composition analysis: 20%

### Approval Workflow

1. **Stage 1 - Concept Selection**: Top 50 from 300+ generations (first human checkpoint)
2. **Stage 2 - Direction Selection**: Top 20 from refinements (second checkpoint)
3. **Stage 3 - Production**: Top 3-5 for final export (final approval)

**Target**: <10 minutes human time per checkpoint.

### Model Knowledge Base

**Architecture**: Static YAML (NOT RAG for v1.0)
- **Location**: `./src/prompt_engine/model_knowledge/`
- **Files**: `stable_diffusion_35.yaml`, `flux_schnell.yaml`, `dalle_3.yaml`
- **Decision**: See `docs/ADR-001-MODEL-KNOWLEDGE-ARCHITECTURE.md`
- **Pattern**: ModelKnowledgeAdapter loads model-specific rules at runtime

---

## Testing Strategy

### Test Levels

1. **Unit Tests** (`tests/unit/`): Test individual functions/classes in isolation
2. **Integration Tests** (`tests/integration/`): Test component interactions
3. **End-to-End Tests** (`tests/e2e/`): Test complete workflows

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=automation.src --cov-report=html

# Run specific test file
pytest tests/unit/test_prompt_engine.py

# Run tests matching pattern
pytest -k "test_color_adherence"

# Run async tests
pytest -v tests/integration/test_generation_pipeline.py
```

### Test Examples

#### Unit Test
```python
# tests/unit/test_color_adherence.py
import pytest
from automation.src.scoring.color_adherence import check_brand_colors

def test_exact_brand_color_match():
    """Test exact brand color detection."""
    image_colors = ["#1A1A1A", "#FF6B35", "#4A90E2"]
    brand_palette = {"forge_black": "#1A1A1A", "spark_orange": "#FF6B35"}

    score = check_brand_colors(image_colors, brand_palette)
    assert score >= 0.95, "Exact matches should score 95%+"
```

#### Integration Test
```python
# tests/integration/test_generation_pipeline.py
import pytest
from automation.src.generation import MultiModelOrchestrator

@pytest.mark.asyncio
async def test_multi_model_generation():
    """Test concurrent generation across multiple models."""
    orchestrator = MultiModelOrchestrator()
    prompts = ["test prompt 1", "test prompt 2"]

    results = await orchestrator.generate_batch(prompts)
    assert len(results) == 2
    assert all(r.model in ["sd35", "flux", "dalle"] for r in results)
```

### Test Coverage Targets

| Component | Target | Status |
|-----------|--------|--------|
| Prompt Engine | 90%+ | Not implemented |
| Generation Pipeline | 80%+ | Not implemented |
| Scoring System | 95%+ | Not implemented |
| Export Pipeline | 85%+ | Not implemented |

---

## Pre-Commit Checklist

Before committing code, ensure:

```bash
# 1. Format code
black --line-length 100 ./src/
ruff check --fix ./src/

# 2. Type check
mypy ./src/

# 3. Run tests
pytest

# 4. Check coverage
pytest --cov=automation.src --cov-report=term-missing

# 5. Verify no sensitive data
git diff --cached | grep -i "api_key\|secret\|password"

# 6. Update documentation if needed
# - Update docstrings
# - Update README.md if API changes
# - Update CHANGELOG.md

# 7. Commit with descriptive message
git add .
git commit -m "feat: add CLIP semantic similarity scoring

- Implemented CLIP model loading and preprocessing
- Added cosine similarity calculation against prompt embeddings
- Cached model weights for performance (30% weight in scoring)
- Added unit tests with 95% coverage

Relates to #25 (Epic #24)

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

# 8. Update GitHub issue status
gh issue comment 25 --body "Implemented CLIP similarity scoring" --repo IAMSamuelRodda/brand-forge
gh issue close 25 --comment "Feature complete: CLIP semantic similarity implemented and tested" --repo IAMSamuelRodda/brand-forge
gh issue edit 25 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge
```

---

## Debugging Guide

### Logging Configuration

```python
# ./src/utils/logging_config.py
import logging
from pathlib import Path

def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
```

### Common Issues

#### Issue: API Rate Limiting
**Symptoms**: 429 HTTP errors from generation APIs
**Solution**: Implement exponential backoff
```python
import asyncio
import aiohttp

async def generate_with_retry(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await api_client.generate(prompt)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise
```

#### Issue: Out of Memory During Batch Processing
**Symptoms**: Process killed, system slowdown
**Solution**: Process in smaller batches
```python
async def generate_in_batches(prompts: list[str], batch_size: int = 10):
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i+batch_size]
        yield await generate_batch(batch)
```

---

## Performance Optimization

### Profiling

```bash
# Profile CPU usage
python -m cProfile -o profile.stats ./src/main.py
python -m pstats profile.stats

# Profile memory usage
pip install memory_profiler
python -m memory_profiler ./src/main.py

# Profile async code
pip install yappi
# Add yappi instrumentation to async functions
```

### Optimization Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Generation throughput | 50+ images/hour | API logs |
| Scoring latency | <5s per image | Performance tests |
| Memory usage | <4GB peak | memory_profiler |
| API cost | <$0.10 per image | Budget tracker |

### Best Practices

1. **AsyncIO for I/O**: Use async/await for all API calls
2. **Batch Processing**: Process images in batches of 10-20
3. **Caching**: Cache CLIP model weights, brand palette calculations
4. **Connection Pooling**: Reuse HTTP connections with aiohttp ClientSession
5. **Progress Tracking**: Log progress every 10% for long-running tasks

---

## Additional Resources

- **Blueprint**: [specs/BLUEPRINT.yaml](specs/BLUEPRINT.yaml) - Complete technical spec
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md) - GitHub workflow guide
- **Status**: [STATUS.md](STATUS.md) - Current milestone progress
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history

---

## Questions or Issues?

- **GitHub Issues**: https://github.com/IAMSamuelRodda/brand-forge/issues
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6

---

**Last Updated**: November 10, 2025
