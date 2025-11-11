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
