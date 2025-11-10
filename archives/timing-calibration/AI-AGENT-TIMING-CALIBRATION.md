# AI Agent Timing Calibration

**Generated**: 2025-11-11
**Purpose**: Project-specific timing data for brand-forge

> **Note**: Full methodology and implementation details are documented in the `github-project-setup` skill (`~/.claude/skills/github-project-setup/SKILL.md` - Section 8: AI-Calibrated Timing Model). This document provides project-specific data only.

---

## Executive Summary

Based on the `embark-quoting-system` MVP completion (81 issues in 7.04 days), AI coding agents operate at **22.8x faster** than traditional human developer estimates.

---

## brand-forge Timeline Projection

| Metric | Human Estimate | AI Projection | Improvement |
|--------|----------------|---------------|-------------|
| **Duration** | 50 days (10 weeks) | 5.8 days (0.8 weeks) | 88% faster |
| **With 1.3x Buffer** | 50 days | 7.6 days (1.1 weeks) | 85% faster |
| **Features per Day** | 0.68 | 5.82 | 8.6x faster |

---

## Usage

See `github-project-setup` skill (Section 8) for:
- Calibration methodology and formulas
- CLI usage examples
- Date population strategies
- Monitoring and validation procedures

**Quick Start**:
```bash
~/.claude/skills/github-project-setup/scripts/create-epic-hierarchy.py \
  specs/BLUEPRINT.yaml \
  --owner IAMSamuelRodda \
  --repo brand-forge
```

---

## Quick Reference

- **Speedup Factor**: 22.8x faster than human estimates
- **Projected Duration**: 15.2 days (with 1.3x buffer)
- **Start Date**: 2025-11-11 (when setup began)
- **Target Completion**: 2025-11-26

**Formula**: `ai_days = human_days × 0.044 × 1.3`

---

## References

- **Full Methodology**: `~/.claude/skills/github-project-setup/SKILL.md` (Section 8)
- **Benchmark**: `/home/samuel/repos/embark-quoting-system`
- **Blueprint**: `specs/BLUEPRINT.yaml`
