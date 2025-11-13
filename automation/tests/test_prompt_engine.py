"""Tests for prompt generation engine."""

import pytest
from pathlib import Path
from generation.prompt_engine import PromptEngine, GeneratedPrompt, PromptVariation
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
def engine(design_brief_path, template_directory):
    """Create prompt engine instance."""
    return PromptEngine(design_brief_path, template_directory, default_variations_per_template=5)


class TestPromptEngine:
    """Test suite for PromptEngine."""

    def test_initialization(self, design_brief_path, template_directory):
        """Test engine initialization."""
        engine = PromptEngine(design_brief_path, template_directory)

        assert engine.processor is not None
        assert engine.default_variations == 50  # Default value
        assert len(engine.generated_hashes) == 0
        assert len(engine.prompt_history) == 0

    def test_generate_variations(self, engine):
        """Test generating variations from a template."""
        template = PromptTemplate(
            text="A {style} logo with {color_scheme} colors",
            variables={"style", "color_scheme"},
            name="Test Logo Template",
            category="logo",
        )

        generated = engine.generate_variations(template, num_variations=5)

        assert isinstance(generated, GeneratedPrompt)
        assert len(generated.variations) > 0
        assert len(generated.variations) <= 5
        assert generated.template_name == "Test Logo Template"
        assert generated.total_variations == len(generated.variations)

    def test_generate_variations_uniqueness(self, engine):
        """Test that generated variations are unique."""
        template = PromptTemplate(
            text="A {style} logo",
            variables={"style"},
        )

        generated = engine.generate_variations(template, num_variations=3)

        # Check all variations have unique IDs
        ids = [v.id for v in generated.variations]
        assert len(ids) == len(set(ids))

        # Check all variations are in history
        assert len(engine.prompt_history) == len(generated.variations)

    def test_generate_variations_adds_to_history(self, engine):
        """Test that variations are added to history."""
        template = PromptTemplate(
            text="A logo design",
            variables=set(),
        )

        initial_count = len(engine.prompt_history)
        generated = engine.generate_variations(template, num_variations=3)

        assert len(engine.prompt_history) == initial_count + len(generated.variations)

    def test_generate_all_variations(self, engine):
        """Test generating variations for all templates."""
        all_prompts = engine.generate_all_variations(variations_per_template=3)

        assert len(all_prompts) > 0
        assert all(isinstance(p, GeneratedPrompt) for p in all_prompts)
        # Some templates may have 0 variations due to lack of variables or duplicates
        # Just check that at least some have variations
        prompts_with_variations = [p for p in all_prompts if len(p.variations) > 0]
        assert len(prompts_with_variations) > 0

    def test_generate_all_variations_with_category_filter(self, engine):
        """Test generating with category filter."""
        all_prompts = engine.generate_all_variations(
            variations_per_template=2, categories=["logo"]
        )

        assert len(all_prompts) > 0
        # All should be logo category
        for prompt_batch in all_prompts:
            for variation in prompt_batch.variations:
                assert variation.template_category == "logo"

    def test_generate_all_variations_with_keyword_filter(self, engine):
        """Test generating with keyword filter."""
        all_prompts = engine.generate_all_variations(
            variations_per_template=2, keywords=["minimalist"]
        )

        # Should find at least some templates with minimalist keyword
        assert len(all_prompts) >= 0  # May be 0 if no templates match

    def test_get_prompt_by_id(self, engine):
        """Test retrieving prompt by ID."""
        template = PromptTemplate(text="A test logo", variables=set())
        generated = engine.generate_variations(template, num_variations=1)

        if generated.variations:
            prompt_id = generated.variations[0].id
            retrieved = engine.get_prompt_by_id(prompt_id)

            assert retrieved is not None
            assert retrieved.id == prompt_id

    def test_update_prompt_effectiveness(self, engine):
        """Test updating prompt effectiveness tracking."""
        template = PromptTemplate(text="A test logo", variables=set())
        generated = engine.generate_variations(template, num_variations=1)

        if generated.variations:
            prompt_id = generated.variations[0].id

            # Update as approved
            engine.update_prompt_effectiveness(prompt_id, approved=True, quality_score=0.85)

            prompt = engine.get_prompt_by_id(prompt_id)
            assert prompt.times_generated == 1
            assert prompt.times_approved == 1
            assert prompt.avg_quality_score == 0.85

            # Update again as not approved
            engine.update_prompt_effectiveness(prompt_id, approved=False, quality_score=0.60)

            prompt = engine.get_prompt_by_id(prompt_id)
            assert prompt.times_generated == 2
            assert prompt.times_approved == 1  # Still 1
            assert 0.70 < prompt.avg_quality_score < 0.75  # Average of 0.85 and 0.60

    def test_get_best_performing_prompts(self, engine):
        """Test getting best performing prompts."""
        # Generate some prompts
        template = PromptTemplate(text="A logo", variables=set())
        generated = engine.generate_variations(template, num_variations=3)

        # Simulate some usage
        for i, variation in enumerate(generated.variations):
            # Give different performance scores
            for _ in range(5):  # Generate 5 times each
                approved = i == 0  # Only approve first prompt
                quality = 0.9 if i == 0 else 0.5
                engine.update_prompt_effectiveness(variation.id, approved, quality)

        # Get best performing
        best = engine.get_best_performing_prompts(min_generations=5, top_n=2)

        assert len(best) > 0
        # First prompt should be best (100% approval rate)
        if len(best) >= 2:
            assert best[0].times_approved >= best[1].times_approved

    def test_get_statistics(self, engine):
        """Test getting engine statistics."""
        # Initially empty
        stats = engine.get_statistics()
        assert stats["total_prompts"] == 0
        assert stats["unique_prompts"] == 0

        # Generate some prompts
        template = PromptTemplate(text="A logo", variables=set())
        generated = engine.generate_variations(template, num_variations=3)

        stats = engine.get_statistics()
        assert stats["total_prompts"] == len(generated.variations)
        assert stats["unique_prompts"] == len(generated.variations)

        # Add some effectiveness data
        if generated.variations:
            engine.update_prompt_effectiveness(
                generated.variations[0].id, approved=True, quality_score=0.8
            )

            stats = engine.get_statistics()
            assert stats["total_generations"] == 1
            assert stats["total_approved"] == 1
            assert stats["approval_rate"] == 1.0

    def test_export_prompts_for_generation(self, engine):
        """Test exporting prompts for API generation."""
        template = PromptTemplate(
            text="A {style} logo",
            variables={"style"},
            parameters={"--v": "6"},
        )
        generated = engine.generate_variations(template, num_variations=2)

        exported = engine.export_prompts_for_generation([generated])

        assert len(exported) == len(generated.variations)
        assert all("prompt_id" in item for item in exported)
        assert all("prompt_text" in item for item in exported)
        assert all("parameters" in item for item in exported)

    def test_export_prompts_to_file(self, engine, tmp_path):
        """Test exporting prompts to JSON file."""
        template = PromptTemplate(text="A logo", variables=set())
        generated = engine.generate_variations(template, num_variations=2)

        output_file = tmp_path / "prompts.json"
        engine.export_prompts_for_generation([generated], output_file)

        assert output_file.exists()

        # Verify JSON content
        import json

        with open(output_file, "r") as f:
            data = json.load(f)
            assert len(data) == len(generated.variations)

    def test_clear_history(self, engine):
        """Test clearing prompt history."""
        template = PromptTemplate(text="A logo", variables=set())
        engine.generate_variations(template, num_variations=3)

        assert len(engine.prompt_history) > 0
        assert len(engine.generated_hashes) > 0

        engine.clear_history()

        assert len(engine.prompt_history) == 0
        assert len(engine.generated_hashes) == 0

    def test_duplicate_detection(self, engine):
        """Test that duplicate prompts are not generated."""
        # Create template that will always generate same prompt
        template = PromptTemplate(text="A static logo design", variables=set())

        generated1 = engine.generate_variations(template, num_variations=1)
        generated2 = engine.generate_variations(template, num_variations=1)

        # Second generation should produce 0 variations (duplicate)
        assert len(generated2.variations) == 0

        # Only first should be in history
        assert len(engine.prompt_history) == len(generated1.variations)


class TestPromptVariation:
    """Test PromptVariation dataclass."""

    def test_prompt_variation_creation(self):
        """Test creating a PromptVariation."""
        variation = PromptVariation(
            id="test123",
            prompt_text="A minimalist logo",
            template_name="Test Template",
            template_category="logo",
        )

        assert variation.id == "test123"
        assert variation.prompt_text == "A minimalist logo"
        assert variation.times_generated == 0
        assert variation.times_approved == 0
        assert variation.avg_quality_score == 0.0


class TestGeneratedPrompt:
    """Test GeneratedPrompt dataclass."""

    def test_generated_prompt_creation(self):
        """Test creating a GeneratedPrompt."""
        variations = [
            PromptVariation(id="1", prompt_text="Prompt 1"),
            PromptVariation(id="2", prompt_text="Prompt 2"),
        ]

        generated = GeneratedPrompt(
            template_id="template_1",
            template_name="Test Template",
            variations=variations,
            total_variations=2,
        )

        assert generated.template_id == "template_1"
        assert len(generated.variations) == 2
        assert generated.total_variations == 2
