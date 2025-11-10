# ADR-001: Model Knowledge Architecture - RAG vs Static YAML

**Status**: Proposed
**Date**: 2025-11-11
**Decision Makers**: Engineering Team
**Context**: Determining the appropriate knowledge management strategy for AI model-specific prompt engineering expertise

---

## Problem Statement

Brand Forge needs to encode prompt engineering expertise for multiple AI models (Stable Diffusion 3.5, Flux Schnell, DALL-E 3) that have different parameter requirements, syntax patterns, and best practices. We need to decide between:

1. **Static YAML Knowledge Base**: Fixed files in git with model-specific rules
2. **RAG with VectorDB**: Dynamic retrieval system that learns from usage and stays current with model updates

---

## Analysis Framework

### 1. Update Frequency Analysis

**Research Findings**:
- **Stable Diffusion**: Major versions every 3-6 months (SD 3.0 → SD 3.5), API stability between versions
- **Flux Schnell**: New model (2024), update cadence unclear, but model is stable
- **DALL-E 3**: Major versions 1-2 years apart (DALL-E 2 → DALL-E 3), API backwards compatible

**Conclusion**: Model knowledge changes **quarterly at fastest**, not daily/weekly.

### 2. Knowledge Query Patterns

**How knowledge is accessed**:
```python
# At generation time (per-image):
prompt = base_template.render(brand_context)
adapted_prompt = adapter.adapt_prompt(prompt, model='sd35')  # ← Knowledge lookup
params = adapter.validate_parameters(base_params)  # ← Knowledge lookup
```

**Query characteristics**:
- **Deterministic**: Same input → same output (no semantic search needed)
- **Predictable**: Known query patterns (adapt_prompt, validate_parameters, suggest_optimizations)
- **Structured**: Model name + function name = exact knowledge retrieval
- **High frequency**: 300-1000 generations/month = 300-1000 lookups/month

### 3. Knowledge Complexity

**What needs to be stored**:
- Prompt structure rules (Subject → Action → Environment → Lighting → Style)
- Parameter constraints (CFG scale: 7-10, steps: 40-60)
- Syntax transformations (remove weight syntax for Flux)
- Common issue → fix mappings

**Complexity characteristics**:
- **Structured data**: Not unstructured text (no semantic search needed)
- **Categorical logic**: IF model=flux THEN remove_weights() (rule-based, not probabilistic)
- **Small dataset**: 3 models × ~50 rules each = 150 rules total (~5-10KB per model)

### 4. Learning Requirements

**What could be learned over time**:
- ✅ Prompt effectiveness (which prompts score highest)
- ✅ Parameter optimization (best CFG/steps for brand assets)
- ✅ Brand-specific patterns (this brand works better with X lighting)
- ❌ Model API changes (requires manual review, not automated learning)

**Observation**: The **learning component** (prompt effectiveness) is separate from **model knowledge** (API constraints).

---

## RAG/VectorDB Evaluation

### When RAG is Appropriate

✅ **Good use cases for RAG**:
1. **Large, unstructured knowledge**: Manuals, documentation, research papers
2. **Semantic search needs**: "Find similar prompts that worked well"
3. **Frequently changing content**: News, social media, dynamic datasets
4. **Unknown query patterns**: Users ask arbitrary questions
5. **Cross-document reasoning**: Synthesize info from multiple sources

### Our Use Case Characteristics

❌ **Our scenario**:
1. **Small, structured knowledge**: 3 YAML files, 5-10KB each
2. **Exact lookups**: model='sd35' → stable_diffusion_35.yaml (no search)
3. **Stable content**: Updates quarterly, not daily
4. **Known query patterns**: 4 functions (adapt, validate, suggest, troubleshoot)
5. **Single-source rules**: Each model's rules are independent

### RAG Trade-offs for Our Case

**Costs** ❌:
- **Infrastructure**: VectorDB hosting (Pinecone, Weaviate, ChromaDB)
- **Embedding costs**: OpenAI embeddings for knowledge chunks (~$0.0001/1K tokens)
- **Query latency**: 50-200ms per retrieval vs <1ms YAML lookup
- **Complexity**: Embedding pipeline, vector search, reranking
- **Maintenance**: Keep embeddings in sync with knowledge changes
- **Determinism loss**: Semantic search may return different results for same query

**Benefits** ✅:
- **Automatic updates**: Could pull latest community best practices
- **Semantic search**: "Find prompts for minimalist logos" → similar examples
- **Cross-model learning**: Discover patterns across SD/Flux/DALL-E
- **Unknown queries**: Handle questions not anticipated in schema

**Verdict**: Costs outweigh benefits for **core model knowledge** (API constraints, syntax rules).

---

## Recommended Architecture

### Hybrid Approach: Static Knowledge + Learning Layer

```
┌────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE ARCHITECTURE                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STATIC MODEL KNOWLEDGE (YAML in git)                    │  │
│  │  • API parameters (CFG scale, steps, aspect ratios)      │  │
│  │  • Syntax rules (weight syntax, negative prompts)        │  │
│  │  • Model capabilities (resolution, strengths/weaknesses) │  │
│  │  • Best practices (prompt structure, common fixes)       │  │
│  │                                                           │  │
│  │  Update: Quarterly (manual, version controlled)          │  │
│  │  Storage: automation/src/prompt_engine/model_knowledge/  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LEARNING LAYER (SQLite analytics)                       │  │
│  │  • Prompt effectiveness tracking (score → prompt)        │  │
│  │  • Parameter optimization (best CFG/steps per context)   │  │
│  │  • Brand-specific patterns (color accuracy per model)    │  │
│  │  • Error pattern detection (common failures → fixes)     │  │
│  │                                                           │  │
│  │  Update: Real-time (from generation results)             │  │
│  │  Storage: automation/data/analytics.db                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OPTIONAL: COMMUNITY KNOWLEDGE (Future - if needed)      │  │
│  │  • RAG/VectorDB for latest community best practices     │  │
│  │  • Weekly scrape of prompt engineering forums           │  │
│  │  • Semantic search for "prompts similar to this"        │  │
│  │                                                           │  │
│  │  Update: Weekly (automated scraping)                     │  │
│  │  Storage: VectorDB (Pinecone/Weaviate) - if ROI proven  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Decision

**RECOMMENDATION: Start with Static YAML Knowledge Base**

### Rationale

1. **Appropriate scale**: 3 models, ~150 rules, 5-10KB each = YAML is perfect
2. **Deterministic needs**: Exact lookups, rule-based logic, no semantic search required
3. **Low update frequency**: Quarterly model changes don't justify real-time RAG
4. **Development velocity**: YAML faster to implement, test, and debug than RAG
5. **Cost efficiency**: $0 for YAML vs $20-50/month for VectorDB + embeddings
6. **Sufficient for MVP**: Prove system value before adding RAG complexity

### When to Revisit (Future Triggers)

Consider adding RAG layer if:

1. **Model count grows**: Supporting 10+ models (SD, Flux, DALL-E, Midjourney v7, Imagen 3, etc.)
2. **Update frequency increases**: Models update weekly instead of quarterly
3. **Semantic search needed**: Users want "find prompts similar to X" functionality
4. **Community integration**: Want to auto-incorporate latest prompt engineering discoveries
5. **Cross-brand learning**: Managing 100+ brands and want to discover patterns across them

### Implementation Plan

**Phase 1 (Now - v1.0)**: Static YAML Knowledge Base
- Create 3 YAML files (SD 3.5, Flux, DALL-E 3)
- Implement ModelKnowledgeLoader + ModelKnowledgeAdapter
- Track prompt effectiveness in SQLite for future learning

**Phase 2 (v1.1)**: Learning Layer
- Analyze prompt effectiveness data
- Build recommendation engine: "For logos, CFG 8.5 performs best on SD 3.5"
- Surface insights to human reviewers

**Phase 3 (v2.0 - if needed)**: RAG Integration
- Evaluate ROI after 6 months of v1.0 usage
- If supporting 10+ models or need semantic search, add VectorDB
- Keep YAML as source of truth, RAG as supplement

---

## Consequences

### Positive ✅

1. **Fast implementation**: YAML-based system ready in days vs weeks for RAG
2. **Zero infrastructure cost**: No VectorDB hosting or embedding API calls
3. **Deterministic behavior**: Same input always produces same output (easier debugging)
4. **Version controlled**: Knowledge changes tracked in git with diffs and rollback
5. **Testable**: Unit tests verify knowledge application without external dependencies
6. **Low latency**: <1ms YAML lookup vs 50-200ms RAG retrieval

### Negative ❌

1. **Manual updates**: Must manually update YAML when models change (quarterly)
2. **No semantic search**: Can't query "prompts for minimalist logos" naturally
3. **No auto-learning**: System won't automatically incorporate community discoveries
4. **Limited scaling**: Managing 50+ models would become cumbersome with YAML

### Mitigation Strategies

1. **Quarterly review cadence**: Schedule reviews aligned with model release cycles
2. **Alerting for model changes**: Monitor model provider changelogs (RSS/API)
3. **Analytics for learning**: Track prompt effectiveness in SQLite for future insights
4. **LLM-assisted maintenance**: Use Claude/GPT-4 to help update YAML files when APIs change

---

## Alternatives Considered

### Alternative 1: Pure RAG from Day 1

**Why not**:
- Premature optimization (3 models don't need VectorDB)
- Higher cost ($20-50/month)
- Slower development (2-3 weeks to build vs 2-3 days for YAML)
- Non-deterministic (harder to debug)

### Alternative 2: Hardcoded Rules in Python

**Why not**:
- Less maintainable (code changes require deployment)
- Not version controlled separately
- Harder for non-developers to update
- No clear separation of concerns

### Alternative 3: LLM as Knowledge Base (Prompt Engineering)

**Why not**:
- API costs for every lookup ($0.001/request × 1000 generations = $1/month)
- Latency (200-500ms per LLM call)
- Non-deterministic responses
- Requires careful prompt engineering (meta-problem)

---

## References

- **Stable Diffusion Updates**: platform.stability.ai/docs/release-notes (quarterly cadence)
- **Flux Schnell**: huggingface.co/black-forest-labs/FLUX.1-schnell (stable model)
- **DALL-E API**: platform.openai.com/docs/models/dall-e-3 (backwards compatible)
- **RAG Best Practices**: "When to Use RAG vs Fine-Tuning" (Pinecone, 2024)
- **Vector DB Comparison**: "VectorDB Benchmarks" (Weaviate, 2024)

---

## Sign-off

**Decision**: Start with Static YAML Knowledge Base (Phase 1)

**Reviewers**: TBD
**Approved By**: TBD
**Next Review**: After v1.0 MVP completion (or 6 months, whichever first)
