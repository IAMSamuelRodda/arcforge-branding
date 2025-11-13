"""
Image generation module for DesignForge.

Handles prompt generation, API integration, and metadata tracking.
"""

from .prompt_engine import PromptEngine, GeneratedPrompt, PromptVariation
from .template_processor import TemplateProcessor, ProcessedTemplate
from .sd_client import (
    StableDiffusionClient,
    GenerationRequest,
    GenerationResult,
    GenerationStats,
    CostTracker,
)

__all__ = [
    # Prompt generation
    "PromptEngine",
    "GeneratedPrompt",
    "PromptVariation",
    "TemplateProcessor",
    "ProcessedTemplate",
    # Image generation
    "StableDiffusionClient",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStats",
    "CostTracker",
]
