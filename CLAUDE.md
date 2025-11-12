# DesignForge - Claude Navigation Guide

> **Purpose**: Essential navigation and project-wide conventions for all agents and subagents.
> **Scope**: Full frontend design automation (brand identity → components → layouts → code)

---

## 🚀 Starting Work

**Before starting any task:**

1. **Review project status**: `cat STATUS.md`
2. **Check contribution workflow**: `cat CONTRIBUTING.md`
3. **View current issues**: `gh issue list --state open --repo IAMSamuelRodda/design-forge`

**Key documents:**
- `STATUS.md` → Current milestone, progress, next steps
- `CONTRIBUTING.md` → Issue hierarchy, branch workflow, progress tracking
- `specs/BLUEPRINT-DESIGNFORGE.yaml` → DesignForge implementation plan (authoritative)
- `specs/BLUEPRINT.yaml` → Original Brand Forge plan (archived)
- `ARCHITECTURE.md` → System architecture and design decisions
- `DEVELOPMENT.md` → Project conventions (naming, sessions, budgets)

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

### Project Conventions

All implementation details documented in **`DEVELOPMENT.md` → Project Conventions**:
- Naming conventions (modules, classes, functions, configs, branches)
- Session organization (path patterns, stages, retention)
- Multi-model strategy (budget, allocation, cost tracking)
- Quality thresholds (color accuracy, scoring correlation, weights)
- Approval workflow (3 stages, <10min checkpoints)
- Model knowledge base (static YAML architecture)

---

## ⚠️ Critical Constraints

1. **Budget**: Stay under $30-60/month per milestone (real-time tracking)
2. **Vertical Slices**: Keep features isolated (generation + scoring + approval + export)
3. **Model Knowledge**: Use static YAML for v1.0-v2.5 (NOT RAG) per ADR-001
4. **Quality**: 95%+ color accuracy, ρ > 0.7 scoring correlation, WCAG 2.1 AA (v2.0+)
5. **Human Time**: <10 minutes per approval checkpoint per milestone
6. **Branch Discipline**: NEVER commit to `main` or `dev` directly
7. **Scope Discipline**: v1.0 Foundation → v1.5 Logos → v2.0 Components → v2.5 Layouts → v3.0 Code

---

## 📋 DesignForge Milestones

### v1.0 Foundation & Core Pipeline (Weeks 1-4) - IN PROGRESS
- Project infrastructure, single-model generation, scoring, approval
- **52 open issues** (1 completed: Issue #3)

### v1.5 Brand Assets Module - HIGH PRIORITY
- Logo generation (300+ variations, 3-5 production-ready)
- **Issues TBD** (generate from BLUEPRINT-DESIGNFORGE.yaml)

### v2.0 Component Library Generation
- Atomic components (buttons, forms, cards, navigation)
- Accessibility scoring (WCAG 2.1 AA)
- **Issues TBD**

### v2.5 Page Layout Generation
- Landing pages, responsive design (mobile-first)
- **Issues TBD**

### v3.0 Code Export & Production
- React/Vue/Svelte, Tailwind optimization
- **Issues TBD**

---

## 🔗 External Links

- **Repository**: https://github.com/IAMSamuelRodda/design-forge
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Issues**: https://github.com/IAMSamuelRodda/design-forge/issues
