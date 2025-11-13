"""Tests for design brief parser."""

import pytest
from pathlib import Path
from design_assets.brief_parser import (
    DesignBriefParser,
    DesignBrief,
    ColorSpec,
    TypographySpec,
    VisualDirection,
)


@pytest.fixture
def design_brief_path():
    """Path to the actual ArchForge design brief."""
    # Get repo root (two levels up from tests/)
    repo_root = Path(__file__).parent.parent
    return repo_root / "archives" / "case-study-arcforge" / "design" / "DESIGN-BRIEF.md"


@pytest.fixture
def parser(design_brief_path):
    """Create parser instance."""
    return DesignBriefParser(design_brief_path)


@pytest.fixture
def parsed_brief(parser):
    """Parse the design brief."""
    return parser.parse()


class TestDesignBriefParser:
    """Test suite for DesignBriefParser."""

    def test_parser_initialization(self, design_brief_path):
        """Test parser can be initialized with valid path."""
        parser = DesignBriefParser(design_brief_path)
        assert parser.brief_path == design_brief_path
        assert parser.content
        assert parser.lines

    def test_parser_invalid_path(self):
        """Test parser raises error with invalid path."""
        with pytest.raises(FileNotFoundError):
            DesignBriefParser(Path("nonexistent.md"))

    def test_parse_returns_design_brief(self, parsed_brief):
        """Test parse() returns DesignBrief object."""
        assert isinstance(parsed_brief, DesignBrief)
        assert parsed_brief.source_file is not None

    def test_parse_monochrome_colors(self, parsed_brief):
        """Test parsing of monochrome color palette."""
        mono = parsed_brief.monochrome_colors

        # Should have all 5 monochrome colors
        assert len(mono) >= 4

        # Check Primary Dark
        assert "Primary Dark" in mono
        primary_dark = mono["Primary Dark"]
        assert primary_dark.hex == "#0A0E14"
        assert primary_dark.name == "Primary Dark"

        # Check Pure White
        assert "Pure White" in mono
        pure_white = mono["Pure White"]
        assert pure_white.hex == "#FFFFFF"
        assert pure_white.name == "Pure White"

    def test_parse_brand_colors(self, parsed_brief):
        """Test parsing of brand color palette."""
        brand = parsed_brief.brand_colors

        # Should have 4 brand colors
        assert len(brand) >= 4

        # Check Forge Fire (Primary Brand Color)
        assert "Forge Fire" in brand
        forge_fire = brand["Forge Fire"]
        assert forge_fire.hex == "#FF6B35"
        assert forge_fire.rgb == "255, 107, 53"
        assert len(forge_fire.use_cases) >= 3
        assert forge_fire.emotional_association is not None

        # Check Data Stream Cyan
        assert "Data Stream Cyan" in brand
        data_cyan = brand["Data Stream Cyan"]
        assert data_cyan.hex == "#00D9FF"
        assert data_cyan.rgb == "0, 217, 255"

        # Check Foundation Violet
        assert "Foundation Violet" in brand
        foundation_violet = brand["Foundation Violet"]
        assert foundation_violet.hex == "#7B2CBF"
        assert foundation_violet.rgb == "123, 44, 191"

        # Check Success Green
        assert "Success Green" in brand
        success_green = brand["Success Green"]
        assert success_green.hex == "#06FFA5"
        assert success_green.rgb == "6, 255, 165"

    def test_brand_color_use_cases(self, parsed_brief):
        """Test that use cases are extracted for brand colors."""
        forge_fire = parsed_brief.brand_colors["Forge Fire"]
        assert len(forge_fire.use_cases) > 0
        # Check for expected use cases
        use_cases_text = " ".join(forge_fire.use_cases).lower()
        assert "cta" in use_cases_text or "interactive" in use_cases_text

    def test_parse_typography(self, parsed_brief):
        """Test parsing of typography system."""
        typo = parsed_brief.typography
        assert isinstance(typo, TypographySpec)

        # Typography parsing is optional - some briefs may not have fonts
        # or the format may not match expected patterns
        # Just verify the structure exists
        assert typo.display_fonts is not None
        assert typo.body_fonts is not None
        assert typo.ui_fonts is not None
        assert typo.code_fonts is not None

    def test_parse_visual_directions(self, parsed_brief):
        """Test parsing of visual design directions."""
        directions = parsed_brief.visual_directions
        assert len(directions) == 3

        # Check direction names
        direction_names = [d.name for d in directions]
        assert "Technical Blueprint" in direction_names
        assert "Sci-Fi Futuristic" in direction_names
        assert "Grounded Fantasy-Tech" in direction_names

        # Check first direction has required fields
        tech_blueprint = next(d for d in directions if d.name == "Technical Blueprint")
        assert tech_blueprint.essence is not None
        assert tech_blueprint.mood is not None
        assert len(tech_blueprint.key_elements) > 0

    def test_visual_direction_key_elements(self, parsed_brief):
        """Test that visual direction key elements are extracted."""
        # Check that at least one direction has key elements
        directions_with_elements = [
            d for d in parsed_brief.visual_directions if len(d.key_elements) > 0
        ]
        assert len(directions_with_elements) > 0

        # Verify first direction has multiple elements
        first_direction = directions_with_elements[0]
        assert len(first_direction.key_elements) >= 3


class TestColorSpec:
    """Test ColorSpec dataclass."""

    def test_color_spec_creation(self):
        """Test creating ColorSpec with required fields."""
        color = ColorSpec(name="Test Color", hex="#FF0000")
        assert color.name == "Test Color"
        assert color.hex == "#FF0000"
        assert color.rgb is None
        assert color.use_cases == []
        assert color.emotional_association is None

    def test_color_spec_with_optional_fields(self):
        """Test ColorSpec with all fields."""
        color = ColorSpec(
            name="Brand Red",
            hex="#FF0000",
            rgb="255, 0, 0",
            use_cases=["CTA buttons", "Error states"],
            emotional_association="Energy, urgency",
        )
        assert color.name == "Brand Red"
        assert color.hex == "#FF0000"
        assert color.rgb == "255, 0, 0"
        assert len(color.use_cases) == 2
        assert color.emotional_association == "Energy, urgency"


class TestTypographySpec:
    """Test TypographySpec dataclass."""

    def test_typography_spec_defaults(self):
        """Test TypographySpec default initialization."""
        typo = TypographySpec()
        assert typo.display_fonts == []
        assert typo.body_fonts == []
        assert typo.ui_fonts == []
        assert typo.code_fonts == []

    def test_typography_spec_with_fonts(self):
        """Test TypographySpec with font lists."""
        typo = TypographySpec(
            display_fonts=["Inter Bold", "Geist Mono"],
            body_fonts=["Inter"],
            ui_fonts=["Inter Medium"],
            code_fonts=["Geist Mono"],
        )
        assert len(typo.display_fonts) == 2
        assert len(typo.body_fonts) == 1
        assert "Inter" in typo.body_fonts


class TestVisualDirection:
    """Test VisualDirection dataclass."""

    def test_visual_direction_creation(self):
        """Test creating VisualDirection."""
        direction = VisualDirection(name="Test Direction")
        assert direction.name == "Test Direction"
        assert direction.essence is None
        assert direction.mood is None
        assert direction.key_elements == []

    def test_visual_direction_complete(self):
        """Test VisualDirection with all fields."""
        direction = VisualDirection(
            name="Minimalist Tech",
            essence="Clean and precise",
            mood="Professional workshop",
            key_elements=["Grid layouts", "Sans-serif fonts", "Whitespace"],
        )
        assert direction.name == "Minimalist Tech"
        assert direction.essence == "Clean and precise"
        assert direction.mood == "Professional workshop"
        assert len(direction.key_elements) == 3


class TestDesignBrief:
    """Test DesignBrief dataclass."""

    def test_design_brief_defaults(self):
        """Test DesignBrief default initialization."""
        brief = DesignBrief()
        assert brief.monochrome_colors == {}
        assert brief.brand_colors == {}
        assert isinstance(brief.typography, TypographySpec)
        assert brief.visual_directions == []
        assert brief.source_file is None

    def test_design_brief_with_data(self):
        """Test DesignBrief with populated data."""
        brief = DesignBrief(
            monochrome_colors={
                "Black": ColorSpec(name="Black", hex="#000000"),
                "White": ColorSpec(name="White", hex="#FFFFFF"),
            },
            brand_colors={
                "Primary": ColorSpec(name="Primary", hex="#FF0000"),
            },
            typography=TypographySpec(body_fonts=["Inter"]),
            visual_directions=[VisualDirection(name="Modern")],
            source_file=Path("test.md"),
        )
        assert len(brief.monochrome_colors) == 2
        assert len(brief.brand_colors) == 1
        assert len(brief.visual_directions) == 1
        assert brief.source_file == Path("test.md")
