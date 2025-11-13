"""
Design asset integration module.

Handles parsing design briefs and loading prompt templates.
"""

from .brief_parser import DesignBriefParser, DesignBrief
from .template_loader import PromptTemplateLoader, PromptTemplate

__all__ = [
    "DesignBriefParser",
    "DesignBrief",
    "PromptTemplateLoader",
    "PromptTemplate",
]
