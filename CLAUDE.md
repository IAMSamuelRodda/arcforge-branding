# Brand Forge - Claude Navigation Guide

> **Purpose**: Essential navigation and project-wide conventions for all agents and subagents.

---

## 🚀 Starting Work

**Before starting any task:**

1. **Review project status**: `cat STATUS.md`
2. **Check contribution workflow**: `cat CONTRIBUTING.md`
3. **View current issues**: `gh issue list --state open --repo IAMSamuelRodda/brand-forge`

**Key documents:**
- `STATUS.md` → Current milestone, progress, next steps
- `CONTRIBUTING.md` → Issue hierarchy, branch workflow, progress tracking
- `specs/BLUEPRINT.yaml` → Complete implementation plan (authoritative source)
- `ARCHITECTURE.md` → System architecture and design decisions

---

## 🎯 Critical Project-Wide Conventions

### Branch Workflow (MANDATORY)

```
main       → Production only (NO direct commits)
  ↑
dev        → Integration only (NO direct commits)
  ↑
feature/*  → All work happens here
```

**Rules:**
1. NEVER commit directly to `main` or `dev`
2. ALWAYS work on feature branches
3. PRs to `dev` auto-merge when checks pass
4. Only promote `dev` → `main` for production deployment

See `CONTRIBUTING.md` → Branch Workflow for full details.

### Multi-Model Cost Constraints

**Budget**: $30-60/month for 500-1000 generations

**Model Allocation:**
- Stable Diffusion 3.5: 70% ($0.004/img)
- Flux Schnell: 20% ($0.003/img)
- DALL-E 3: 10% ($0.04/img)

**Real-time cost tracking required** with alerts at 50%, 75%, 90% of budget.

### Model Knowledge Base

**Architecture**: Static YAML (NOT RAG for v1.0)
- Location: `automation/src/prompt_engine/model_knowledge/`
- Files: `stable_diffusion_35.yaml`, `flux_schnell.yaml`, `dalle_3.yaml`
- Decision rationale: `docs/ADR-001-MODEL-KNOWLEDGE-ARCHITECTURE.md`

### Quality Thresholds

- **Brand color accuracy**: 95%+
- **Scoring correlation**: Spearman's ρ > 0.7 vs human judgment
- **Scoring weights**: CLIP (30%), Color (25%), Aesthetic (25%), Composition (20%)

### Naming Conventions

- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase` (e.g., `ModelKnowledgeAdapter`)
- **Functions**: `snake_case` (e.g., `generate_variations`)
- **Config files**: `kebab-case.yaml` (e.g., `brand-criteria.yaml`)
- **Feature branches**: `feature/epic-N-description` or `feature/issue-N-description`

### Session Organization

- **Path pattern**: `results/{session_id}/{stage}/`
- **Stages**: `stage_1_concept`, `stage_2_refinement`, `stage_3_production`
- **Retention**: 30 days (automated cleanup)

### Approval Workflow

1. **Stage 1 - Concept**: Top 50 from 300+ generations
2. **Stage 2 - Refinement**: Top 20 from refinements
3. **Stage 3 - Production**: Top 3-5 for export

Target: <10 minutes human time per checkpoint.

---

## 📂 Project Structure

```
automation/
├── config/              # YAML configs (models, brand criteria, scoring)
├── src/
│   ├── generation/      # Prompt engine, API clients, queue
│   ├── scoring/         # CLIP, color, aesthetic, composition
│   ├── approval/        # CLI viewer, Flask dashboard
│   ├── refinement/      # img2img engine
│   ├── export/          # Upscaling, background removal, vectorization
│   ├── database/        # SQLite schema, CRUD
│   └── prompt_engine/
│       └── model_knowledge/  # YAML knowledge base
├── web/                 # Flask app, Tailwind templates
├── results/             # Generated images (gitignored)
└── data/                # SQLite databases (gitignored)
```

---

## ⚠️ Critical Constraints

1. **Budget**: Stay under $30-60/month (real-time tracking)
2. **Vertical Slices**: Keep features isolated (generation + scoring + approval)
3. **Model Knowledge**: Use static YAML for v1.0 (NOT RAG) per ADR-001
4. **Quality**: 95%+ color accuracy, ρ > 0.7 scoring correlation
5. **Human Time**: <10 minutes per approval checkpoint
6. **Branch Discipline**: NEVER commit to `main` or `dev` directly

---

## 🔗 External Links

- **Repository**: https://github.com/IAMSamuelRodda/brand-forge
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Issues**: https://github.com/IAMSamuelRodda/brand-forge/issues
