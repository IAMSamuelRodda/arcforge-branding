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
from .multi_backend_client import MultiBackendClient, BackendStats
from .backends import (
    GenerationBackend,
    LocalGPUBackend,
    ReplicateBackend,
    BackendConfig,
)

__all__ = [
    # Prompt generation
    "PromptEngine",
    "GeneratedPrompt",
    "PromptVariation",
    "TemplateProcessor",
    "ProcessedTemplate",
    # Image generation (single backend)
    "StableDiffusionClient",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStats",
    "CostTracker",
    # Multi-backend generation
    "MultiBackendClient",
    "BackendStats",
    # Backends
    "GenerationBackend",
    "LocalGPUBackend",
    "ReplicateBackend",
    "BackendConfig",
]
