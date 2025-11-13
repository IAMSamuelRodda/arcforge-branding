"""Dataclass models for model configuration."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModelConfig:
    """Configuration for a single AI model."""

    name: str
    enabled: bool
    provider: str
    model_id: str
    api_key: str
    parameters: Dict[str, any] = field(default_factory=dict)
    rate_limiting: Dict[str, int] = field(default_factory=dict)
    cost_per_generation: float = 0.0


@dataclass
class GenerationStrategy:
    """Strategy for generation (primary model, fallbacks, retries)."""

    primary_model: str
    fallback_models: List[str] = field(default_factory=list)
    max_retries: int = 3
    backoff_multiplier: float = 2.0


@dataclass
class BudgetConfig:
    """Budget tracking and limits."""

    monthly_limit_usd: float
    alert_thresholds: List[Dict[str, any]] = field(default_factory=list)
    track_per_model: bool = True
    track_per_session: bool = True
