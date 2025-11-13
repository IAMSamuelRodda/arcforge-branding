"""Dataclass models for scoring weights configuration."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DimensionWeight:
    """Weight configuration for a single scoring dimension."""

    weight: float
    description: str
    min_score: float = 0.0
    max_score: float = 1.0
    target_score: float = 0.7


@dataclass
class CompositeScore:
    """Composite score calculation configuration."""

    formula: str = "weighted_average"
    passing_threshold: float = 0.70
    production_threshold: float = 0.80


@dataclass
class ScoringWeights:
    """Complete scoring weights configuration."""

    dimensions: Dict[str, DimensionWeight] = field(default_factory=dict)
    composite: CompositeScore = field(default_factory=CompositeScore)
