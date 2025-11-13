# DesignForge - AI-Powered Frontend Design Automation

![GitHub Issues](https://img.shields.io/github/issues/IAMSamuelRodda/design-forge)
![GitHub Project](https://img.shields.io/badge/project-roadmap-blue)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-planning-yellow)

**Fully automated frontend design system** that transforms design briefs into production-ready visual assets and framework-specific code through AI-driven workflows with human approval checkpoints.

> **Scope**: Brand identity (v1.5) → Atomic components (v2.0) → Page layouts (v2.5) → Production code (v3.0)

```
Design Brief → AI Generation → Quality Scoring → Human Approval → Code Export
     ↓              ↓                 ↓                 ↓              ↓
  Logos      Components/Layouts   Accessibility    Refinement    React/Vue/CSS
```

---

## Overview

DesignForge eliminates manual iteration in frontend design development by:

- **Generating complete design systems** from brand identity through production code
- **v1.5 Brand Assets**: 300+ logo variations with 95%+ color accuracy ($30-60/month)
- **v2.0 Component Library**: Buttons, forms, cards, navigation with accessibility scoring
- **v2.5 Page Layouts**: Responsive landing pages and app layouts (mobile-first)
- **v3.0 Code Export**: React, Vue, Svelte, Tailwind with production optimization
- **Reducing human time to <10 min/checkpoint** across 3 approval stages per milestone

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    AUTOMATION PIPELINE                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │  Design Briefs  │  (DESIGN-BRIEF.md)                        │
│  │  Prompt Temps   │  (PROMPT-TEMPLATES-*.md)                  │
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
git clone https://github.com/IAMSamuelRodda/brand-forge.git
cd brand-forge

# Create virtual environment
python3 -m venv ./.venv
source ./.venv/bin/activate

# Install dependencies (when available)
uv pip install -r ./requirements.txt

# Configure API keys
cp ./config/config.example.yaml ./config/config.yaml
# Edit config.yaml with your API keys

# Run generation pipeline (when implemented)
python src/main.py
```

---

## Usage

### Workflow (Per Milestone)

1. **Design Input**: Load specifications (design brief + prompt templates + component specs)
2. **Prompt Generation**: Process templates with variables (brand/component/layout-specific)
3. **AI Generation**: Stable Diffusion 3.5 (v1.0-v2.5), Claude 3.5 Sonnet (v3.0 code)
4. **Quality Scoring**: CLIP, color, aesthetic, composition, accessibility (WCAG 2.1 AA)
5. **Human Approval**: 3 checkpoints per milestone (concept → refinement → final)
6. **Export**: Multi-format images (v1.5-v2.5), framework code (v3.0)

### Configuration

Edit `./config/config.yaml`:

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

## Project Structure (Vertical Slice Architecture)

Each feature slice contains its own code, tests, and documentation:

```
design-forge/
├── 
│   ├── src/
│   │   ├── prompt_engine/       # Template processing + docs
│   │   ├── generation/          # AI generation API + docs
│   │   ├── scoring/             # Quality + accessibility scoring + docs
│   │   ├── refinement/          # Iterative refinement + docs
│   │   ├── approval/            # Human approval UI + docs
│   │   ├── export/              # Image/code export + docs
│   │   └── code_gen/            # Framework code generation (v3.0)
│   ├── config/                  # Configuration files
│   ├── web/                     # Flask dashboard
│   └── tests/                   # Test suites
├── specs/
│   ├── BLUEPRINT-DESIGNFORGE.yaml  # DesignForge specification
│   └── BLUEPRINT.yaml              # Original (archived)
├── archives/
│   └── case-study-arcforge/     # ArcForge test case materials
├── STATUS.md                    # Progress tracking
├── CLAUDE.md                    # Project conventions
├── CONTRIBUTING.md              # Workflow guide
└── README.md                    # This file
```

**Documentation Philosophy**: Each feature directory contains its own `README.md` with:
- Feature overview and architecture
- API documentation
- Usage examples
- Testing approach

**No separate `/docs` folder** - documentation lives with the code it documents.

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

### Milestone 2: v1.5 Brand Assets Module (HIGH PRIORITY)
- [ ] Logo generation (300+ variations, 3-5 production-ready)
- [ ] Multi-format exports (SVG, PNG, WebP)
- [ ] Brand package delivery

### Milestone 3: v2.0 Component Library Generation
- [ ] Atomic components (buttons, forms, cards, navigation)
- [ ] Accessibility scoring (WCAG 2.1 AA)
- [ ] Component variations and states

### Milestone 4: v2.5 Page Layout Generation
- [ ] Landing pages and app layouts
- [ ] Responsive design (mobile-first)
- [ ] Component composition

### Milestone 5: v3.0 Code Export & Production
- [ ] HTML/CSS/JS generation
- [ ] React/Vue/Svelte exports
- [ ] Tailwind optimization

**Current Status**: v1.0 Foundation (52 issues open, Epic #1 ready to start)

**View Progress**: https://github.com/users/IAMSamuelRodda/projects/6

---

## License

Proprietary - All rights reserved.

**Owner**: Samuel Rodda
**Created**: November 2025
**Status**: Active Development

---

## Links

- **GitHub Repository**: https://github.com/IAMSamuelRodda/design-forge
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Issues**: https://github.com/IAMSamuelRodda/design-forge/issues
- **Blueprint**: [specs/BLUEPRINT-DESIGNFORGE.yaml](specs/BLUEPRINT-DESIGNFORGE.yaml)

---

**Last Updated**: November 12, 2025
