"""Dataclass models for brand criteria configuration."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ColorAccuracy:
    """Color accuracy criteria and thresholds."""

    delta_e_threshold: float
    strict_delta_e_threshold: float
    target_accuracy: float


@dataclass
class AestheticQuality:
    """Aesthetic quality criteria."""

    min_score: float
    target_score: float
    dimensions: Dict[str, float] = field(default_factory=dict)


@dataclass
class Composition:
    """Composition and layout criteria."""

    aspect_ratio_preferred: str
    aspect_ratio_accepted: List[str] = field(default_factory=list)
    min_symmetry_score: float = 0.3


@dataclass
class BrandCriteria:
    """Complete brand criteria configuration."""

    color_accuracy: ColorAccuracy
    aesthetic_quality: AestheticQuality
    composition: Composition
