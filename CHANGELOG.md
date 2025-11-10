# Changelog

All notable changes to the ArcForge Branding Automation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

#### Milestone 1: v1.0 Foundation & Core Pipeline (Weeks 1-4)
- Project foundation and infrastructure setup
- Basic generation pipeline (single model: Stable Diffusion 3.5)
- Quality scoring and filtering system
- Human approval interface

#### Milestone 2: v1.1 Multi-Model & Iterative Refinement (Weeks 5-8)
- Multi-model generation pipeline (SD 3.5, Flux, DALL-E)
- Iterative refinement pipeline (img2img)
- Production finalization and export

#### Milestone 3: v1.2 Production Polish & Documentation (Weeks 9-10)
- Testing and quality assurance
- Performance optimization
- Documentation and user experience

---

## [0.1.0-alpha] - 2025-11-10

### Added

#### Project Structure
- Created comprehensive blueprint at `specs/BLUEPRINT.yaml` with 10 epics, 35 features, 96 tasks
- Established 3 milestones over 10-week timeline
- Defined multi-model AI pipeline architecture

#### Design Assets
- Integrated existing design briefs (1,157-line `design/DESIGN-BRIEF.md`)
- Included 6 engineered prompt templates (`design/MIDJOURNEY-PROMPTS-*.md`)
- Established brand palette: Forge Black (#1A1A1A), Spark Orange (#FF6B35), Vector Blue (#4A90E2)

#### GitHub Project Management
- Created public repository: https://github.com/IAMSamuelRodda/arcforge-branding
- Generated 125 GitHub issues:
  - 10 epics (type: epic)
  - 34 features (type: feature)
  - 81 tasks (type: task)
- Established 115 parent-child relationships (hierarchical sub-issues)
- Created 3 milestones with timeline markers
- Set up Project #6: "ArcForge Branding Automation Roadmap" with date fields
- Added 20+ standardized labels (type, status, priority)

#### Documentation
- Created `CONTRIBUTING.md` with agent workflow guide and gh CLI reference
- Created comprehensive `README.md` with architecture diagrams, installation guide, usage instructions
- Created `STATUS.md` with current milestone progress tracking
- Created this `CHANGELOG.md` for version history
- Created `.gitignore` for Python, results, data exclusions
- Created `.gitattributes` for line ending normalization
- Created `DEVELOPMENT.md` with development environment setup and testing strategy

### Technical Decisions

#### Multi-Model Strategy
- **Stable Diffusion 3.5**: 70% allocation (bulk generation, $0.004/img)
- **Flux Schnell**: 20% allocation (quality comparisons, $0.003/img)
- **DALL-E 3**: 10% allocation (text-heavy fallback, $0.04/img)
- **Rationale**: Cost optimization within $30-60/month budget for 500-1000 generations

#### Quality Scoring Weights
- CLIP semantic similarity: 30%
- Brand color adherence: 25%
- Aesthetic prediction: 25%
- Composition analysis: 20%
- **Target**: Spearman's ρ > 0.70 correlation with human judgment

#### Human Approval Checkpoints
1. **Concept Selection**: Top 50 from 300+ generations
2. **Direction Selection**: Top 20 from refinements
3. **Final Approval**: Top 3-5 for production

#### Technology Stack
- **Language**: Python 3.11+
- **Package Manager**: uv (10-100x faster than pip)
- **Database**: SQLite (metadata, lineage, approval tracking)
- **Web UI**: Flask/Streamlit
- **Progress Tracking**: GitHub Issues + Projects (hierarchical sub-issues)

### Context

This release establishes the complete planning foundation for an automated branding development system that:
- Eliminates manual iteration in brand asset generation
- Reduces human involvement to <10 minutes per checkpoint
- Achieves 95%+ brand color accuracy
- Operates within budget constraints
- Delivers production-ready assets with upscaling, background removal, vectorization

**Trigger**: User requested Midjourney integration planning. After research revealed TOS violations and lack of official API, pivoted to legal alternatives (Stable Diffusion, Flux, DALL-E) while maintaining automation goals.

---

## Version History

- **[0.1.0-alpha]** (2025-11-10): Initial planning phase - blueprint, GitHub setup, documentation
- **[Unreleased]**: Future milestones planned over 10 weeks

---

## Links

- **GitHub Repository**: https://github.com/IAMSamuelRodda/arcforge-branding
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Blueprint**: [specs/BLUEPRINT.yaml](specs/BLUEPRINT.yaml)
