# DesignForge Automation

> **Status**: v1.0 Foundation - In Progress
> **Last Updated**: November 12, 2025

Automated frontend design system that transforms design briefs into production-ready visual assets and framework-specific code.

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (ALWAYS use uv, not pip)
uv pip install -r requirements.txt

# Verify installation
python smoke_test.py
```

### Expected Output

```
DesignForge Dependency Smoke Test
==================================================
✓ PyTorch              - OK
✓ TorchVision          - OK
✓ Transformers         - OK
...

Summary:
  Passed: 29/29
  Failed: 0/29
```

## Dependencies

### Core ML/AI (2.5GB+)
- **PyTorch 2.1.2**: Deep learning framework (CLIP, aesthetic models)
- **Transformers 4.36.2**: HuggingFace models for semantic similarity
- **OpenCV 4.9.0**: Computer vision (color extraction, composition analysis)
- **Scikit-learn 1.3.2**: K-means clustering for brand color detection

### Image Generation APIs
- **OpenAI 1.6.1**: DALL-E 3, CLIP embeddings
- **Replicate 0.25.0**: Flux Schnell API
- **aiohttp 3.9.1**: Async HTTP for concurrent API calls

### Web & CLI
- **Flask 3.0.0**: Human approval dashboard
- **Rich 13.7.0**: Terminal UI components (image gallery, progress bars)

### Database
- **SQLAlchemy 2.0.23**: ORM for prompt→image→score lineage tracking
- **aiosqlite 0.19.0**: Async SQLite operations

### Testing & Quality
- **pytest 7.4.3**: Test framework
- **ruff 0.1.8**: Linter (replaces flake8, black, isort)
- **mypy 1.7.1**: Type checking

## Directory Structure

```
automation/
├── .venv/                      # Virtual environment (gitignored)
├── config/                     # YAML configuration files
├── src/                        # Source code (vertical slices)
│   ├── prompt_engine/          # Template processing
│   ├── generation/             # AI generation pipeline
│   ├── scoring/                # Quality + accessibility scoring
│   ├── refinement/             # Iterative refinement
│   ├── approval/               # Human approval interface
│   ├── export/                 # Multi-format export
│   └── code_gen/               # Framework code generation (v3.0)
├── web/                        # Flask dashboard
├── data/                       # SQLite database (gitignored)
├── results/                    # Generated images (gitignored)
├── requirements.txt            # Pinned dependencies
├── smoke_test.py               # Import verification
└── README.md                   # This file
```

## Next Steps

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow and [STATUS.md](../STATUS.md) for current progress.

---

**Milestone**: v1.0 Foundation & Core Pipeline (52 issues)
**Blueprint**: [specs/BLUEPRINT-DESIGNFORGE.yaml](../specs/BLUEPRINT-DESIGNFORGE.yaml)
