# ArcForge Branding Automation

![GitHub Issues](https://img.shields.io/github/issues/IAMSamuelRodda/arcforge-branding)
![GitHub Project](https://img.shields.io/badge/project-roadmap-blue)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-planning-yellow)

**Fully automated branding development system** that generates 300+ brand asset variations from design briefs with multi-model AI pipelines, quality scoring, and human checkpoints.

```
Design Brief → AI Generation → Quality Scoring → Human Approval → Production Export
```

---

## Overview

ArcForge Branding Automation eliminates manual iteration in brand asset development by:

- **Generating 500-1000 variations/month** across 3 AI models (Stable Diffusion 3.5, Flux Schnell, DALL-E 3)
- **Scoring quality automatically** with 4-dimensional weighted system (95%+ brand color accuracy)
- **Reducing human time to <10 min/checkpoint** across 3 approval stages
- **Delivering production-ready assets** with upscaling, background removal, vectorization
- **Operating within $30-60/month budget** using cost-optimized model allocation

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    AUTOMATION PIPELINE                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │  Design Briefs  │  (DESIGN-BRIEF.md)                        │
│  │  Prompt Temps   │  (MIDJOURNEY-PROMPTS-*.md)                │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Prompt Engine   │  (Template processor + variable subst)    │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────┐           │
│  │      Multi-Model Generation Pipeline            │           │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────┐│           │
│  │  │ SD 3.5 (70%) │  │ Flux (20%)   │  │ DALL-E ││           │
│  │  │ $0.004/img   │  │ $0.003/img   │  │ (10%)  ││           │
│  │  └──────┬───────┘  └──────┬───────┘  └────┬───┘│           │
│  └─────────┼──────────────────┼───────────────┼────┘           │
│           ▼                  ▼               ▼                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │         Quality Scoring System                  │           │
│  │  • CLIP similarity (30%)                        │           │
│  │  • Brand color adherence (25%)                  │           │
│  │  • Aesthetic prediction (25%)                   │           │
│  │  • Composition analysis (20%)                   │           │
│  └────────┬────────────────────────────────────────┘           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Human Approval  │  (3 checkpoints: concept → direction      │
│  │   Interface     │   → final approval)                       │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────┐           │
│  │      Production Export Pipeline                 │           │
│  │  • Real-ESRGAN upscaling (4K)                   │           │
│  │  • rembg background removal                     │           │
│  │  • potrace vectorization (SVG)                  │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11+ | AsyncIO orchestration, API integration |
| **Package Manager** | uv | 10-100x faster than pip |
| **AI Models** | Stable Diffusion 3.5, Flux Schnell, DALL-E 3 | Multi-model generation for quality/cost balance |
| **Quality Scoring** | CLIP, scikit-learn, OpenCV | Semantic similarity, color analysis, composition |
| **Database** | SQLite | Metadata tracking, lineage, approval status |
| **Web UI** | Flask/Streamlit | Human approval interface |
| **Production Export** | Real-ESRGAN, rembg, potrace | Upscaling, background removal, vectorization |
| **Progress Tracking** | GitHub Issues + Projects | Hierarchical sub-issues with automatic roll-up |

---

## Installation

### Prerequisites

- Python 3.11+
- uv package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git
- GitHub CLI (`gh`) with `project` and `read:project` scopes

### Quick Start

```bash
# Clone repository
git clone https://github.com/IAMSamuelRodda/arcforge-branding.git
cd arcforge-branding

# Create virtual environment
python3 -m venv automation/.venv
source automation/.venv/bin/activate

# Install dependencies (when available)
uv pip install -r automation/requirements.txt

# Configure API keys
cp automation/config/config.example.yaml automation/config/config.yaml
# Edit config.yaml with your API keys

# Run generation pipeline (when implemented)
python automation/src/main.py
```

---

## Usage

### 6-Stage Workflow

1. **Design Input**: Load brand specifications from `design/DESIGN-BRIEF.md` and prompt templates from `design/MIDJOURNEY-PROMPTS-*.md`

2. **Prompt Generation**: Process templates with brand palette and visual direction variables

3. **Multi-Model Generation**: Generate 70% via Stable Diffusion 3.5, 20% via Flux Schnell, 10% via DALL-E 3

4. **Quality Scoring**: Score all outputs with weighted 4-dimensional system (target: 80+ correlation with human judgment)

5. **Human Approval**: Review top-scoring variations at 3 checkpoints:
   - **Concept Selection** (top 50 from 300+ generations)
   - **Direction Selection** (top 20 from refinements)
   - **Final Approval** (top 3-5 for production)

6. **Production Export**: Upscale to 4K, remove backgrounds, vectorize to SVG

### Configuration

Edit `automation/config/config.yaml`:

```yaml
models:
  stable_diffusion:
    enabled: true
    api_key: "your-api-key"
    allocation: 0.70  # 70% of generations
  flux:
    enabled: true
    api_key: "your-api-key"
    allocation: 0.20  # 20% of generations
  dalle:
    enabled: true
    api_key: "your-openai-key"
    allocation: 0.10  # 10% of generations

quality_scoring:
  weights:
    semantic_similarity: 0.30
    brand_color_adherence: 0.25
    aesthetic_prediction: 0.25
    composition_analysis: 0.20
  thresholds:
    minimum_score: 0.65
    brand_color_accuracy: 0.95

budget:
  monthly_limit: 60.00  # USD
  generation_target: 500  # images/month
```

---

## Project Structure

```
arcforge-branding/
├── automation/
│   ├── config/
│   │   └── config.yaml              # API keys, model settings, weights
│   ├── src/
│   │   ├── prompt_engine/           # Template processing
│   │   ├── generation/              # Multi-model API integration
│   │   ├── scoring/                 # Quality scoring system
│   │   ├── refinement/              # Iterative img2img
│   │   └── export/                  # Production export pipeline
│   ├── web/
│   │   └── approval_interface/      # Flask/Streamlit UI
│   ├── results/                     # Generated images (gitignored)
│   ├── data/                        # SQLite database (gitignored)
│   └── requirements.txt             # Python dependencies
├── design/
│   ├── DESIGN-BRIEF.md              # Brand specifications (1,157 lines)
│   └── MIDJOURNEY-PROMPTS-*.md      # 6 engineered prompt templates
├── assets/
│   └── approved/                    # Production-ready exports
├── specs/
│   └── BLUEPRINT.yaml               # Complete technical spec (1,824 lines)
├── CONTRIBUTING.md                  # Agent workflow guide
├── STATUS.md                        # Current milestone progress
├── CHANGELOG.md                     # Version history
├── DEVELOPMENT.md                   # Development setup & testing
└── README.md                        # This file
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Generations/Month** | 500-1000 | API call logs |
| **Brand Color Accuracy** | 95%+ | Color distance (ΔE < 5) |
| **Quality Score Correlation** | ρ > 0.70 | Spearman's rank vs human judgment |
| **Human Time/Checkpoint** | <10 min | UI interaction logs |
| **Production Assets** | 3-5 logos | Final export count |
| **Monthly Cost** | $30-60 | API billing reports |

---

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Development environment setup
- Testing strategy
- Code style guidelines
- Pre-commit checklist

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- GitHub Issues workflow
- Progress tracking with gh CLI
- Epic-milestone mapping
- Agent coordination

---

## Roadmap

### Milestone 1: v1.0 Foundation & Core Pipeline (Weeks 1-4)
- [ ] Epic #1: Project Foundation & Infrastructure
- [ ] Epic #11: Basic Generation Pipeline (Single Model)
- [ ] Epic #24: Quality Scoring & Filtering System
- [ ] Epic #39: Human Approval Interface

### Milestone 2: v1.1 Multi-Model & Iterative Refinement (Weeks 5-8)
- [ ] Epic #50: Multi-Model Generation Pipeline
- [ ] Epic #64: Iterative Refinement Pipeline
- [ ] Epic #75: Production Finalization & Export

### Milestone 3: v1.2 Production Polish & Documentation (Weeks 9-10)
- [ ] Epic #91: Testing & Quality Assurance
- [ ] Epic #102: Performance Optimization
- [ ] Epic #112: Documentation & User Experience

**Current Status**: Planning phase (Milestone 1 not started)

**View Progress**: https://github.com/users/IAMSamuelRodda/projects/6

---

## License

Proprietary - All rights reserved.

**Owner**: Samuel Rodda
**Created**: November 2025
**Status**: Active Development

---

## Links

- **GitHub Repository**: https://github.com/IAMSamuelRodda/arcforge-branding
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Issues**: https://github.com/IAMSamuelRodda/arcforge-branding/issues
- **Blueprint**: [specs/BLUEPRINT.yaml](specs/BLUEPRINT.yaml)

---

**Last Updated**: November 10, 2025
