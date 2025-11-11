# Source Code Directory

This directory contains the core Python modules for the Brand Forge automation system.

## Modules

- `generation/` - Prompt engine, API clients, and queue management
- `scoring/` - CLIP, color detection, aesthetic, and composition analyzers
- `approval/` - CLI viewer, web dashboard, and state management
- `refinement/` - img2img engine and parameter exploration
- `export/` - Upscaling, background removal, vectorization, format conversion
- `database/` - SQLite schema, CRUD operations, and query interface
- `prompt_engine/` - Template processing and model-specific prompt adaptation
  - `model_knowledge/` - YAML knowledge base for model-specific best practices

## Architecture

Each module operates as an independent vertical slice with minimal cross-dependencies, enabling parallel development and isolated testing.
