# Configuration Directory

This directory contains YAML configuration files for the Brand Forge automation system.

## Files

- `models.yaml` - Model endpoints, API keys, and rate limiting configurations
- `brand-criteria.yaml` - Brand color tolerances and quality thresholds
- `scoring-weights.yaml` - Weighted scoring dimensions (CLIP, color, aesthetic, composition)
- `budget.yaml` - Monthly cost limits and alert thresholds

## Usage

Configuration files are loaded at runtime by the generation and scoring systems. API keys should be stored in environment variables or a separate `.env` file (gitignored).
