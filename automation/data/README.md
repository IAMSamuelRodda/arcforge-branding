# Data Directory

This directory contains the SQLite database and metadata for the Brand Forge system.

## Files

- `brand-forge.db` - Main SQLite database
- `analytics.db` - Analytics and performance tracking database

## Database Schema

### Main Database (brand-forge.db)

- `generations` - Generated image metadata
- `prompts` - Prompt templates and variations
- `scores` - Quality scores (CLIP, color, aesthetic, composition)
- `approvals` - Human approval decisions and feedback
- `refinements` - img2img refinement chains
- `exports` - Production export records

### Analytics Database (analytics.db)

- `prompt_effectiveness` - Prompt performance metrics
- `model_performance` - Per-model success rates
- `cost_tracking` - API usage and costs
- `user_preferences` - User profile and learning data (v2.0+)

## Gitignore

This directory is gitignored to protect sensitive user data and prevent large database files from being committed to the repository.
