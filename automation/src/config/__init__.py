"""
Configuration management module for DesignForge.

Provides centralized access to configuration files for:
- Model endpoints and API keys
- Brand criteria and thresholds
- Scoring weights and dimensions
"""

from .loader import ConfigLoader, ConfigError
from .models import ModelConfig, GenerationStrategy, BudgetConfig
from .brand import BrandCriteria, ColorAccuracy, AestheticQuality, Composition
from .scoring import ScoringWeights, DimensionWeight, CompositeScore

__all__ = [
    "ConfigLoader",
    "ConfigError",
    "ModelConfig",
    "GenerationStrategy",
    "BudgetConfig",
    "BrandCriteria",
    "ColorAccuracy",
    "AestheticQuality",
    "Composition",
    "ScoringWeights",
    "DimensionWeight",
    "CompositeScore",
]
