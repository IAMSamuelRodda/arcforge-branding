"""Tests for template processor."""

import pytest
from pathlib import Path
from generation.template_processor import TemplateProcessor, ProcessedTemplate
from design_assets.template_loader import PromptTemplate


@pytest.fixture
def design_brief_path():
    """Path to test design brief."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / "archives" / "case-study-arcforge" / "design" / "DESIGN-BRIEF.md"


@pytest.fixture
def template_directory():
    """Path to test template directory."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / "archives" / "case-study-arcforge" / "design"


@pytest.fixture
def processor(design_brief_path, template_directory):
    """Create template processor with loaded data."""
    return TemplateProcessor(design_brief_path, template_directory)


class TestTemplateProcessor:
    """Test suite for TemplateProcessor."""

    def test_initialization(self, design_brief_path, template_directory):
        """Test processor initialization."""
        processor = TemplateProcessor(design_brief_path, template_directory)

        assert processor.design_brief is not None
        assert len(processor.templates) > 0

    def test_load_design_brief(self, design_brief_path):
        """Test loading design brief."""
        processor = TemplateProcessor()
        processor.load_design_brief(design_brief_path)

        assert processor.design_brief is not None
        assert len(processor.design_brief.brand_colors) == 4
        assert len(processor.design_brief.visual_directions) == 3

    def test_load_templates(self, template_directory):
        """Test loading prompt templates."""
        processor = TemplateProcessor()
        processor.load_templates(template_directory)

        assert len(processor.templates) > 0

    def test_get_available_variables(self, processor):
        """Test getting available variables from design brief."""
        variables = processor.get_available_variables()

        # Should have color variables
        assert "color_scheme" in variables
        assert "primary_color" in variables

        # Should have style variables
        assert "style" in variables
        assert "mood" in variables

        # Check specific brand colors
        assert "Forge Fire" in variables["color_scheme"]
        assert "Data Stream Cyan" in variables["color_scheme"]

    def test_process_template_basic(self, processor):
        """Test processing a basic template."""
        # Create a simple test template
        template = PromptTemplate(
            text="A {style} logo with {color_scheme} colors",
            variables={"style", "color_scheme"},
            name="Test Template",
            category="logo",
        )

        processed = processor.process_template(template)

        assert isinstance(processed, ProcessedTemplate)
        assert processed.original_template == template
        assert "{style}" not in processed.prompt_text
        assert "{color_scheme}" not in processed.prompt_text
        assert len(processed.substitutions) >= 2

    def test_process_template_custom_variables(self, processor):
        """Test processing with custom variable substitutions."""
        template = PromptTemplate(
            text="A {style} logo with {custom_var}",
            variables={"style", "custom_var"},
        )

        custom_vars = {"custom_var": "special feature"}
        processed = processor.process_template(template, custom_vars)

        assert "special feature" in processed.prompt_text
        assert processed.substitutions["custom_var"] == "special feature"

    def test_process_template_model_format_sd(self, processor):
        """Test processing for Stable Diffusion format."""
        template = PromptTemplate(
            text="A minimalist logo",
            variables=set(),
        )

        processed = processor.process_template(template, None, "stable_diffusion")

        # Should add quality tags
        assert "masterpiece" in processed.prompt_text.lower() or "high quality" in processed.prompt_text.lower()

    def test_process_template_model_format_dalle(self, processor):
        """Test processing for DALL-E format."""
        template = PromptTemplate(
            text="A minimalist logo --v 6 --s 250",
            variables=set(),
            parameters={"--v": "6", "--s": "250"},
        )

        processed = processor.process_template(template, None, "dalle")

        # Should remove parameter flags for DALL-E
        assert "--v" not in processed.prompt_text
        assert "--s" not in processed.prompt_text

    def test_process_all_templates(self, processor):
        """Test processing all loaded templates."""
        processed_list = processor.process_all_templates()

        assert len(processed_list) > 0
        assert all(isinstance(p, ProcessedTemplate) for p in processed_list)

    def test_process_all_templates_with_limit(self, processor):
        """Test processing templates with limit."""
        processed_list = processor.process_all_templates(limit=3)

        assert len(processed_list) <= 3

    def test_generate_variable_combinations(self, processor):
        """Test generating variable combinations."""
        template = PromptTemplate(
            text="A {style} logo with {color_scheme}",
            variables={"style", "color_scheme"},
        )

        combinations = processor.generate_variable_combinations(template, num_variations=10)

        assert len(combinations) > 0
        assert len(combinations) <= 10
        # Each combination should have keys for template variables
        for combo in combinations:
            assert "style" in combo or "color_scheme" in combo

    def test_generate_variable_combinations_unique(self, processor):
        """Test that variable combinations are unique."""
        template = PromptTemplate(
            text="A {style} logo",
            variables={"style"},
        )

        combinations = processor.generate_variable_combinations(template, num_variations=5)

        # Convert to tuples for set comparison
        combo_tuples = [tuple(sorted(c.items())) for c in combinations]
        assert len(combo_tuples) == len(set(combo_tuples))  # All unique

    def test_get_template_by_category(self, processor):
        """Test filtering templates by category."""
        logo_templates = processor.get_template_by_category("logo")

        assert len(logo_templates) > 0
        assert all(t.category == "logo" for t in logo_templates)

    def test_get_templates_by_keywords(self, processor):
        """Test filtering templates by keywords."""
        minimalist_templates = processor.get_templates_by_keywords(["minimalist"])

        assert len(minimalist_templates) > 0
        assert all(
            "minimalist" in [k.lower() for k in t.keywords]
            for t in minimalist_templates
        )

    def test_format_for_model_stable_diffusion(self, processor):
        """Test formatting for Stable Diffusion."""
        prompt = "A clean logo design"
        formatted = processor._format_for_model(prompt, "stable_diffusion")

        assert "masterpiece" in formatted.lower() or "high quality" in formatted.lower()

    def test_format_for_model_flux(self, processor):
        """Test formatting for Flux."""
        prompt = "A clean logo design"
        formatted = processor._format_for_model(prompt, "flux")

        # Flux keeps prompt mostly as-is
        assert "clean logo design" in formatted.lower()
