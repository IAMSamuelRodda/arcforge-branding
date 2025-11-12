"""
Prompt template loader for reading and processing prompt template files.

Loads prompt templates from Markdown files and extracts:
- Template prompts with variable placeholders
- Variable names (e.g., {style}, {color_scheme})
- Metadata (versions, categories, keywords)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class PromptTemplate:
    """A single prompt template with variables."""

    text: str
    variables: Set[str] = field(default_factory=set)
    name: Optional[str] = None
    category: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    parameters: Dict[str, str] = field(default_factory=dict)  # e.g., {"--v": "6", "--s": "250"}


@dataclass
class PromptTemplateCollection:
    """Collection of prompt templates from a single file."""

    templates: List[PromptTemplate] = field(default_factory=list)
    source_file: Optional[Path] = None
    title: Optional[str] = None
    description: Optional[str] = None


class PromptTemplateLoader:
    """Loader for prompt template files (PROMPT-TEMPLATES-*.md)."""

    # Regex patterns
    VARIABLE_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
    CODE_BLOCK_PATTERN = re.compile(r"```\n?(.*?)\n?```", re.DOTALL)
    PARAMETER_PATTERN = re.compile(r"(--[a-z]+)\s+([^\s\-][^\s]*)")

    def __init__(self, template_path: Path):
        """
        Initialize loader with path to template file.

        Args:
            template_path: Path to PROMPT-TEMPLATES-*.md file
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        self.content = self.template_path.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")

    def load(self) -> PromptTemplateCollection:
        """
        Load and parse prompt templates from file.

        Returns:
            PromptTemplateCollection with all parsed templates
        """
        collection = PromptTemplateCollection(source_file=self.template_path)

        # Extract title from first heading
        for line in self.lines[:5]:
            if line.startswith("#"):
                collection.title = line.lstrip("#").strip()
                break

        # Extract all prompt templates
        collection.templates = self._extract_templates()

        return collection

    def _extract_templates(self) -> List[PromptTemplate]:
        """Extract all prompt templates from the file."""
        templates = []

        # Find all code blocks (prompts are typically in code blocks)
        code_blocks = self.CODE_BLOCK_PATTERN.findall(self.content)

        for block in code_blocks:
            prompt_text = block.strip()

            if not prompt_text or len(prompt_text) < 10:
                # Skip empty or very short blocks
                continue

            template = PromptTemplate(text=prompt_text)

            # Extract variables
            template.variables = set(self.VARIABLE_PATTERN.findall(prompt_text))

            # Extract Midjourney/SD parameters (--v, --s, --style, etc.)
            template.parameters = dict(self.PARAMETER_PATTERN.findall(prompt_text))

            # Try to find template name from preceding heading or comment
            template.name = self._find_template_name(prompt_text)

            # Extract keywords from preceding context
            template.keywords = self._extract_keywords(prompt_text)

            # Classify category based on content
            template.category = self._classify_category(prompt_text)

            templates.append(template)

        return templates

    def _find_template_name(self, prompt_text: str) -> Optional[str]:
        """
        Find the name/identifier for a prompt template.

        Looks for patterns like "### Prompt 1A:", "## PRIMARY PROMPTS", etc.
        """
        # Search backwards from the prompt position
        prompt_pos = self.content.find(prompt_text)
        if prompt_pos == -1:
            return None

        # Look at the 500 characters before the prompt
        context = self.content[max(0, prompt_pos - 500) : prompt_pos]
        context_lines = context.split("\n")

        # Find last heading before the prompt
        for line in reversed(context_lines):
            if line.startswith("#"):
                # Extract name from heading
                name = line.lstrip("#").strip()
                # Clean up common patterns
                name = re.sub(r"Prompt\s+\d+[A-Z]?:", "", name).strip()
                name = re.sub(r"⭐+", "", name).strip()
                return name if name else None

        return None

    def _extract_keywords(self, prompt_text: str) -> List[str]:
        """
        Extract relevant keywords from the prompt.

        Identifies style keywords like: minimalist, isometric, vector, technical, etc.
        """
        keywords = []

        # Common style keywords
        style_keywords = [
            "minimalist",
            "vector",
            "isometric",
            "geometric",
            "technical",
            "monochrome",
            "bold",
            "clean",
            "precision",
            "modern",
            "futuristic",
            "sci-fi",
            "holographic",
            "blueprint",
            "schematic",
            "line art",
            "flat",
            "3d",
            "emblem",
            "icon",
            "logo",
        ]

        prompt_lower = prompt_text.lower()
        for keyword in style_keywords:
            if keyword in prompt_lower:
                keywords.append(keyword)

        return keywords

    def _classify_category(self, prompt_text: str) -> str:
        """
        Classify the template into a category based on content.

        Categories: logo, icon, illustration, ui, pattern, etc.
        """
        prompt_lower = prompt_text.lower()

        if "logo" in prompt_lower:
            return "logo"
        elif "icon" in prompt_lower:
            return "icon"
        elif "illustration" in prompt_lower:
            return "illustration"
        elif "pattern" in prompt_lower:
            return "pattern"
        elif "ui" in prompt_lower or "interface" in prompt_lower:
            return "ui"
        elif "background" in prompt_lower:
            return "background"
        else:
            return "general"

    @staticmethod
    def load_directory(directory_path: Path) -> List[PromptTemplateCollection]:
        """
        Load all prompt template files from a directory.

        Args:
            directory_path: Path to directory containing template files

        Returns:
            List of PromptTemplateCollection objects
        """
        directory = Path(directory_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        collections = []
        seen_files = set()

        # Find all template files (PROMPT-TEMPLATES*.md, MIDJOURNEY-PROMPTS*.md, etc.)
        patterns = ["PROMPT-TEMPLATES*.md", "MIDJOURNEY-PROMPTS*.md", "*PROMPT*.md"]

        for pattern in patterns:
            for template_file in directory.glob(pattern):
                # Skip if already processed
                if template_file in seen_files:
                    continue
                seen_files.add(template_file)

                try:
                    loader = PromptTemplateLoader(template_file)
                    collection = loader.load()
                    collections.append(collection)
                except Exception as e:
                    # Log error but continue loading other files
                    print(f"Warning: Failed to load {template_file}: {e}")

        return collections

    def substitute_variables(
        self, template: PromptTemplate, variables: Dict[str, str]
    ) -> str:
        """
        Substitute variables in a template with provided values.

        Args:
            template: PromptTemplate to process
            variables: Dictionary mapping variable names to values

        Returns:
            Prompt text with variables substituted
        """
        result = template.text

        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, var_value)

        return result
