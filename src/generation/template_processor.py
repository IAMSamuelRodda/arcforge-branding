"""Template processor for converting design briefs into prompts."""

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from design_assets.brief_parser import DesignBriefParser, DesignBrief
from design_assets.template_loader import (
    PromptTemplateLoader,
    PromptTemplate,
    PromptTemplateCollection,
)


@dataclass
class ProcessedTemplate:
    """A prompt template processed with design brief variables."""

    original_template: PromptTemplate
    prompt_text: str  # Final prompt with variables substituted
    substitutions: Dict[str, str] = field(default_factory=dict)  # What was substituted
    model_format: str = "stable_diffusion"  # Target model format
    parameters: Dict[str, str] = field(default_factory=dict)  # Model parameters


class TemplateProcessor:
    """Processes prompt templates with design brief data."""

    def __init__(
        self,
        design_brief_path: Optional[Path] = None,
        template_directory: Optional[Path] = None,
    ):
        """
        Initialize template processor.

        Args:
            design_brief_path: Path to DESIGN-BRIEF.md file
            template_directory: Path to directory with prompt templates
        """
        self.design_brief: Optional[DesignBrief] = None
        self.templates: List[PromptTemplateCollection] = []

        if design_brief_path:
            self.load_design_brief(design_brief_path)

        if template_directory:
            self.load_templates(template_directory)

    def load_design_brief(self, brief_path: Path) -> None:
        """Load design brief from file."""
        parser = DesignBriefParser(brief_path)
        self.design_brief = parser.parse()

    def load_templates(self, template_directory: Path) -> None:
        """Load all prompt templates from directory."""
        self.templates = PromptTemplateLoader.load_directory(template_directory)

    def get_available_variables(self) -> Dict[str, List[str]]:
        """
        Get all available variables from design brief.

        Returns:
            Dictionary mapping variable names to possible values
        """
        if not self.design_brief:
            return {}

        variables = {}

        # Color variables
        if self.design_brief.brand_colors:
            variables["color_scheme"] = list(self.design_brief.brand_colors.keys())
            variables["primary_color"] = list(self.design_brief.brand_colors.keys())

            # Individual color variables
            for name, color in self.design_brief.brand_colors.items():
                var_name = name.lower().replace(" ", "_")
                variables[var_name] = [color.hex]

        # Visual direction variables
        if self.design_brief.visual_directions:
            variables["style"] = [d.name for d in self.design_brief.visual_directions]
            variables["mood"] = [
                d.mood for d in self.design_brief.visual_directions if d.mood
            ]
            variables["essence"] = [
                d.essence for d in self.design_brief.visual_directions if d.essence
            ]

        # Typography variables
        if self.design_brief.typography:
            typo = self.design_brief.typography
            if typo.display_fonts:
                variables["display_font"] = typo.display_fonts
            if typo.body_fonts:
                variables["body_font"] = typo.body_fonts
            if typo.code_fonts:
                variables["code_font"] = typo.code_fonts

        return variables

    def process_template(
        self,
        template: PromptTemplate,
        custom_variables: Optional[Dict[str, str]] = None,
        model_format: str = "stable_diffusion",
    ) -> ProcessedTemplate:
        """
        Process a single template with design brief variables.

        Args:
            template: PromptTemplate to process
            custom_variables: Optional custom variable substitutions
            model_format: Target model format ('stable_diffusion', 'dalle', 'flux')

        Returns:
            ProcessedTemplate with substituted variables
        """
        if not self.design_brief:
            raise ValueError("Design brief not loaded")

        # Start with template text
        prompt_text = template.text
        substitutions = {}

        # Get available variables
        available_vars = self.get_available_variables()

        # Substitute each variable
        for var_name in template.variables:
            # Check for custom variable first
            if custom_variables and var_name in custom_variables:
                value = custom_variables[var_name]
            # Then check available variables from design brief
            elif var_name in available_vars:
                # Pick first value (or random for variation)
                values = available_vars[var_name]
                value = values[0] if values else f"{{{var_name}}}"
            else:
                # Leave unmatched variables as-is
                continue

            # Perform substitution
            placeholder = f"{{{var_name}}}"
            prompt_text = prompt_text.replace(placeholder, value)
            substitutions[var_name] = value

        # Format for target model
        prompt_text = self._format_for_model(prompt_text, model_format)

        # Copy parameters from template
        parameters = template.parameters.copy()

        return ProcessedTemplate(
            original_template=template,
            prompt_text=prompt_text,
            substitutions=substitutions,
            model_format=model_format,
            parameters=parameters,
        )

    def process_all_templates(
        self,
        model_format: str = "stable_diffusion",
        limit: Optional[int] = None,
    ) -> List[ProcessedTemplate]:
        """
        Process all loaded templates.

        Args:
            model_format: Target model format
            limit: Optional limit on number of templates to process

        Returns:
            List of processed templates
        """
        processed = []

        for collection in self.templates:
            for template in collection.templates:
                try:
                    processed_template = self.process_template(template, None, model_format)
                    processed.append(processed_template)

                    if limit and len(processed) >= limit:
                        return processed
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Failed to process template '{template.name}': {e}")
                    continue

        return processed

    def generate_variable_combinations(
        self,
        template: PromptTemplate,
        num_variations: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Generate multiple variable combinations for a template.

        Args:
            template: Template to generate variations for
            num_variations: Number of variations to generate

        Returns:
            List of variable dictionaries
        """
        available_vars = self.get_available_variables()
        combinations = []
        seen_combinations = set()

        attempts = 0
        max_attempts = num_variations * 10  # Prevent infinite loops

        while len(combinations) < num_variations and attempts < max_attempts:
            attempts += 1
            combination = {}

            # For each variable in template, pick a random value
            for var_name in template.variables:
                if var_name in available_vars:
                    values = available_vars[var_name]
                    if values:
                        combination[var_name] = random.choice(values)

            # Create a hashable representation to check for duplicates
            combo_key = tuple(sorted(combination.items()))
            if combo_key not in seen_combinations:
                seen_combinations.add(combo_key)
                combinations.append(combination)

        return combinations

    def _format_for_model(self, prompt: str, model_format: str) -> str:
        """
        Format prompt for specific model requirements.

        Args:
            prompt: Raw prompt text
            model_format: Target model

        Returns:
            Formatted prompt
        """
        if model_format == "stable_diffusion":
            # Stable Diffusion: Emphasize quality tags
            if "masterpiece" not in prompt.lower():
                prompt = f"{prompt}, masterpiece, high quality"

        elif model_format == "dalle":
            # DALL-E: More descriptive, natural language
            # Remove parameters like --v, --s
            import re
            prompt = re.sub(r"--[a-z]+\s+\S+", "", prompt).strip()

        elif model_format == "flux":
            # Flux: Similar to SD but optimized for speed
            # Keep it concise
            pass

        return prompt.strip()

    def get_template_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates matching a category."""
        templates = []
        for collection in self.templates:
            for template in collection.templates:
                if template.category == category:
                    templates.append(template)
        return templates

    def get_templates_by_keywords(self, keywords: List[str]) -> List[PromptTemplate]:
        """Get all templates matching any of the keywords."""
        templates = []
        keywords_lower = [k.lower() for k in keywords]

        for collection in self.templates:
            for template in collection.templates:
                template_keywords_lower = [k.lower() for k in template.keywords]
                if any(kw in template_keywords_lower for kw in keywords_lower):
                    templates.append(template)

        return templates
