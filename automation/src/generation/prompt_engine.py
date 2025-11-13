"""Prompt generation engine with variation and tracking."""

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .template_processor import TemplateProcessor, ProcessedTemplate
from design_assets.template_loader import PromptTemplate


@dataclass
class PromptVariation:
    """A single prompt variation."""

    id: str  # Unique hash of prompt content
    prompt_text: str
    template_name: Optional[str] = None
    template_category: Optional[str] = None
    substitutions: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, str] = field(default_factory=dict)
    model_format: str = "stable_diffusion"
    created_at: datetime = field(default_factory=datetime.now)

    # Effectiveness tracking
    times_generated: int = 0
    times_approved: int = 0
    avg_quality_score: float = 0.0


@dataclass
class GeneratedPrompt:
    """A batch of generated prompt variations."""

    template_id: str
    template_name: str
    variations: List[PromptVariation] = field(default_factory=list)
    total_variations: int = 0
    created_at: datetime = field(default_factory=datetime.now)


class PromptEngine:
    """Engine for generating prompt variations from templates."""

    def __init__(
        self,
        design_brief_path: Path,
        template_directory: Path,
        default_variations_per_template: int = 50,
    ):
        """
        Initialize prompt engine.

        Args:
            design_brief_path: Path to design brief
            template_directory: Path to prompt templates
            default_variations_per_template: Default number of variations to generate
        """
        self.processor = TemplateProcessor(design_brief_path, template_directory)
        self.default_variations = default_variations_per_template

        # Track generated prompts to avoid duplicates
        self.generated_hashes: Set[str] = set()
        self.prompt_history: List[PromptVariation] = []

    def generate_variations(
        self,
        template: PromptTemplate,
        num_variations: Optional[int] = None,
        model_format: str = "stable_diffusion",
    ) -> GeneratedPrompt:
        """
        Generate multiple variations of a prompt template.

        Args:
            template: Template to generate variations from
            num_variations: Number of variations (defaults to engine default)
            model_format: Target model format

        Returns:
            GeneratedPrompt with all variations
        """
        num_variations = num_variations or self.default_variations
        variations = []

        # Generate variable combinations
        var_combinations = self.processor.generate_variable_combinations(
            template, num_variations
        )

        # Process each combination
        for i, var_combo in enumerate(var_combinations):
            try:
                processed = self.processor.process_template(
                    template, var_combo, model_format
                )

                # Create variation
                variation = self._create_variation(processed, template)

                # Check for duplicates
                if variation.id not in self.generated_hashes:
                    self.generated_hashes.add(variation.id)
                    self.prompt_history.append(variation)
                    variations.append(variation)
                else:
                    # Try to generate a different variation
                    continue

            except Exception as e:
                print(f"Warning: Failed to generate variation {i+1}: {e}")
                continue

        return GeneratedPrompt(
            template_id=self._generate_template_id(template),
            template_name=template.name or "Unnamed Template",
            variations=variations,
            total_variations=len(variations),
        )

    def generate_all_variations(
        self,
        variations_per_template: Optional[int] = None,
        model_format: str = "stable_diffusion",
        categories: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ) -> List[GeneratedPrompt]:
        """
        Generate variations for all loaded templates.

        Args:
            variations_per_template: Variations per template
            model_format: Target model format
            categories: Optional filter by categories
            keywords: Optional filter by keywords

        Returns:
            List of GeneratedPrompt objects
        """
        all_prompts = []

        # Get templates to process
        templates = []
        for collection in self.processor.templates:
            templates.extend(collection.templates)

        # Apply filters
        if categories:
            templates = [t for t in templates if t.category in categories]

        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            templates = [
                t
                for t in templates
                if any(kw in [tk.lower() for tk in t.keywords] for kw in keywords_lower)
            ]

        # Generate variations for each template
        for template in templates:
            try:
                generated = self.generate_variations(
                    template, variations_per_template, model_format
                )
                all_prompts.append(generated)
            except Exception as e:
                print(f"Warning: Failed to generate prompts for template: {e}")
                continue

        return all_prompts

    def get_best_performing_prompts(
        self, min_generations: int = 5, top_n: int = 10
    ) -> List[PromptVariation]:
        """
        Get best performing prompts based on approval rate.

        Args:
            min_generations: Minimum times generated to be considered
            top_n: Number of top prompts to return

        Returns:
            List of top performing prompts
        """
        # Filter by minimum generations
        eligible = [
            p for p in self.prompt_history if p.times_generated >= min_generations
        ]

        # Sort by approval rate (with quality score as tiebreaker)
        def score_prompt(p: PromptVariation) -> float:
            approval_rate = p.times_approved / p.times_generated if p.times_generated > 0 else 0
            return approval_rate * 100 + p.avg_quality_score

        eligible.sort(key=score_prompt, reverse=True)

        return eligible[:top_n]

    def get_prompt_by_id(self, prompt_id: str) -> Optional[PromptVariation]:
        """Get a prompt variation by its ID."""
        for prompt in self.prompt_history:
            if prompt.id == prompt_id:
                return prompt
        return None

    def update_prompt_effectiveness(
        self,
        prompt_id: str,
        approved: bool,
        quality_score: Optional[float] = None,
    ) -> None:
        """
        Update effectiveness tracking for a prompt.

        Args:
            prompt_id: ID of the prompt
            approved: Whether the generated image was approved
            quality_score: Optional quality score (0-1)
        """
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            return

        prompt.times_generated += 1
        if approved:
            prompt.times_approved += 1

        if quality_score is not None:
            # Update rolling average
            n = prompt.times_generated
            prompt.avg_quality_score = (
                (prompt.avg_quality_score * (n - 1)) + quality_score
            ) / n

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about generated prompts."""
        if not self.prompt_history:
            return {
                "total_prompts": 0,
                "unique_prompts": 0,
                "avg_quality_score": 0.0,
                "approval_rate": 0.0,
            }

        total_generated = sum(p.times_generated for p in self.prompt_history)
        total_approved = sum(p.times_approved for p in self.prompt_history)
        avg_quality = sum(p.avg_quality_score for p in self.prompt_history) / len(
            self.prompt_history
        )

        return {
            "total_prompts": len(self.prompt_history),
            "unique_prompts": len(self.generated_hashes),
            "total_generations": total_generated,
            "total_approved": total_approved,
            "avg_quality_score": avg_quality,
            "approval_rate": total_approved / total_generated if total_generated > 0 else 0.0,
        }

    def _create_variation(
        self, processed: ProcessedTemplate, original_template: PromptTemplate
    ) -> PromptVariation:
        """Create a PromptVariation from a processed template."""
        # Generate unique ID from prompt content
        prompt_id = self._generate_prompt_hash(processed.prompt_text)

        return PromptVariation(
            id=prompt_id,
            prompt_text=processed.prompt_text,
            template_name=original_template.name,
            template_category=original_template.category,
            substitutions=processed.substitutions,
            parameters=processed.parameters,
            model_format=processed.model_format,
        )

    def _generate_prompt_hash(self, prompt_text: str) -> str:
        """Generate a unique hash for a prompt."""
        return hashlib.md5(prompt_text.encode()).hexdigest()[:16]

    def _generate_template_id(self, template: PromptTemplate) -> str:
        """Generate a unique ID for a template."""
        content = f"{template.name}:{template.text}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def export_prompts_for_generation(
        self,
        prompts: List[GeneratedPrompt],
        output_path: Optional[Path] = None,
    ) -> List[Dict[str, any]]:
        """
        Export prompts in format ready for image generation API.

        Args:
            prompts: List of GeneratedPrompt objects
            output_path: Optional path to save JSON export

        Returns:
            List of prompt dictionaries ready for API
        """
        export_data = []

        for generated_prompt in prompts:
            for variation in generated_prompt.variations:
                export_data.append(
                    {
                        "prompt_id": variation.id,
                        "prompt_text": variation.prompt_text,
                        "template_name": variation.template_name,
                        "category": variation.template_category,
                        "model_format": variation.model_format,
                        "parameters": variation.parameters,
                        "substitutions": variation.substitutions,
                    }
                )

        # Optionally save to file
        if output_path:
            import json

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)

        return export_data

    def clear_history(self) -> None:
        """Clear prompt history and generated hashes (for testing)."""
        self.generated_hashes.clear()
        self.prompt_history.clear()
