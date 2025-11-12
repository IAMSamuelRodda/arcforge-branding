"""
Design brief parser for extracting brand specifications from DESIGN-BRIEF.md files.

Extracts:
- Color palette (monochrome + brand colors)
- Typography system (fonts for display, body, UI, code)
- Visual directions (style aesthetics)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ColorSpec:
    """Specification for a single color."""

    name: str
    hex: str = ""
    rgb: Optional[str] = None
    use_cases: List[str] = field(default_factory=list)
    emotional_association: Optional[str] = None


@dataclass
class TypographySpec:
    """Typography specifications for different text purposes."""

    display_fonts: List[str] = field(default_factory=list)
    body_fonts: List[str] = field(default_factory=list)
    ui_fonts: List[str] = field(default_factory=list)
    code_fonts: List[str] = field(default_factory=list)


@dataclass
class VisualDirection:
    """Visual design direction/aesthetic."""

    name: str
    essence: Optional[str] = None
    mood: Optional[str] = None
    key_elements: List[str] = field(default_factory=list)


@dataclass
class DesignBrief:
    """Parsed design brief containing all brand specifications."""

    monochrome_colors: Dict[str, ColorSpec] = field(default_factory=dict)
    brand_colors: Dict[str, ColorSpec] = field(default_factory=dict)
    typography: TypographySpec = field(default_factory=TypographySpec)
    visual_directions: List[VisualDirection] = field(default_factory=list)
    source_file: Optional[Path] = None


class DesignBriefParser:
    """Parser for DESIGN-BRIEF.md files."""

    # Regex patterns
    HEX_PATTERN = re.compile(r"`#([0-9A-Fa-f]{6})`")
    RGB_PATTERN = re.compile(r"`(\d+,\s*\d+,\s*\d+)`")
    FONT_PATTERN = re.compile(r"\*\*([A-Za-z\s]+(?:Mono|Sans|Serif)?)\*\*")

    def __init__(self, brief_path: Path):
        """
        Initialize parser with path to design brief.

        Args:
            brief_path: Path to DESIGN-BRIEF.md file
        """
        self.brief_path = Path(brief_path)
        if not self.brief_path.exists():
            raise FileNotFoundError(f"Design brief not found: {brief_path}")

        self.content = self.brief_path.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")

    def parse(self) -> DesignBrief:
        """
        Parse the design brief and extract all specifications.

        Returns:
            DesignBrief object with parsed data
        """
        brief = DesignBrief(source_file=self.brief_path)

        # Parse color system
        brief.monochrome_colors = self._parse_monochrome_colors()
        brief.brand_colors = self._parse_brand_colors()

        # Parse typography
        brief.typography = self._parse_typography()

        # Parse visual directions
        brief.visual_directions = self._parse_visual_directions()

        return brief

    def _parse_monochrome_colors(self) -> Dict[str, ColorSpec]:
        """Extract monochrome color palette."""
        colors = {}

        # Find monochrome section
        in_monochrome = False
        for line in self.lines:
            if "Foundation: Monochrome Base" in line or "Monochrome Base" in line:
                in_monochrome = True
                continue

            if in_monochrome and line.startswith("###"):
                # End of monochrome section
                break

            if in_monochrome and "-" in line and "#" in line:
                # Parse color line: "- **Primary Dark:** `#0A0E14` (description)"
                name_match = re.search(r"\*\*([^*]+)\*\*", line)
                hex_match = self.HEX_PATTERN.search(line)

                if name_match and hex_match:
                    name = name_match.group(1).strip().replace(":", "")
                    hex_code = f"#{hex_match.group(1)}"

                    # Extract description in parentheses
                    desc_match = re.search(r"\(([^)]+)\)", line)
                    description = desc_match.group(1) if desc_match else None

                    colors[name] = ColorSpec(
                        name=name,
                        hex=hex_code,
                        emotional_association=description,
                    )

        return colors

    def _parse_brand_colors(self) -> Dict[str, ColorSpec]:
        """Extract brand color palette."""
        colors = {}

        # Find brand color section
        in_brand_colors = False
        current_color = None

        for i, line in enumerate(self.lines):
            if "Brand Color Palette" in line:
                in_brand_colors = True
                continue

            if in_brand_colors and line.startswith("###") and "Color Application" in line:
                # End of brand colors section
                break

            if in_brand_colors and line.startswith("####"):
                # New color: "#### Color 1: **Forge Fire** (Primary Brand Color)"
                name_match = re.search(r"\*\*([^*]+)\*\*", line)
                if name_match:
                    color_name = name_match.group(1).strip()
                    current_color = ColorSpec(name=color_name)
                    colors[color_name] = current_color

            if current_color and "**Hex:**" in line:
                hex_match = self.HEX_PATTERN.search(line)
                if hex_match:
                    current_color.hex = f"#{hex_match.group(1)}"

            if current_color and "**RGB:**" in line:
                rgb_match = self.RGB_PATTERN.search(line)
                if rgb_match:
                    current_color.rgb = rgb_match.group(1)

            if current_color and "**Use Cases:**" in line:
                # Collect use cases from following bullet points
                for j in range(i + 1, min(i + 10, len(self.lines))):
                    if self.lines[j].strip().startswith("-"):
                        use_case = self.lines[j].strip()[1:].strip()
                        current_color.use_cases.append(use_case)
                    elif self.lines[j].startswith("**"):
                        break

            if current_color and "**Emotional Association:**" in line:
                # Extract text after the label
                parts = line.split("**Emotional Association:**")
                if len(parts) > 1:
                    current_color.emotional_association = parts[1].strip()

        return colors

    def _parse_typography(self) -> TypographySpec:
        """Extract typography specifications."""
        typo = TypographySpec()

        in_typography = False
        current_section = None

        for line in self.lines:
            if "Typography System" in line or "Font Hierarchy" in line:
                in_typography = True
                continue

            if in_typography and line.startswith("###") and "Responsive" in line:
                # End of typography section
                break

            # Detect sections
            if in_typography and line.startswith("####"):
                if "Display" in line or "Headings" in line:
                    current_section = "display"
                elif "Body" in line or "Content" in line:
                    current_section = "body"
                elif "UI" in line or "Interface" in line:
                    current_section = "ui"
                elif "Code" in line or "Technical" in line:
                    current_section = "code"

            # Extract font names
            if in_typography and "**Font" in line:
                fonts = self.FONT_PATTERN.findall(line)
                if current_section == "display":
                    typo.display_fonts.extend(fonts)
                elif current_section == "body":
                    typo.body_fonts.extend(fonts)
                elif current_section == "ui":
                    typo.ui_fonts.extend(fonts)
                elif current_section == "code":
                    typo.code_fonts.extend(fonts)

        # Deduplicate
        typo.display_fonts = list(dict.fromkeys(typo.display_fonts))
        typo.body_fonts = list(dict.fromkeys(typo.body_fonts))
        typo.ui_fonts = list(dict.fromkeys(typo.ui_fonts))
        typo.code_fonts = list(dict.fromkeys(typo.code_fonts))

        return typo

    def _parse_visual_directions(self) -> List[VisualDirection]:
        """Extract visual design directions."""
        directions = []

        in_directions = False
        current_direction = None

        for line in self.lines:
            if "## Visual Directions" in line:
                in_directions = True
                continue

            if in_directions and line.startswith("##") and "Motion Design" in line:
                # End of visual directions section
                break

            if in_directions and line.startswith("###") and "Direction" in line:
                # New direction: "### Direction 1: **Technical Blueprint**"
                name_match = re.search(r"\*\*([^*]+)\*\*", line)
                if name_match:
                    direction_name = name_match.group(1).strip()
                    current_direction = VisualDirection(name=direction_name)
                    directions.append(current_direction)

            if current_direction:
                if "**Essence:**" in line:
                    parts = line.split("**Essence:**")
                    if len(parts) > 1:
                        current_direction.essence = parts[1].strip()

                if "**Mood:**" in line:
                    parts = line.split("**Mood:**")
                    if len(parts) > 1:
                        current_direction.mood = parts[1].strip()

                if "**Key Visual Elements:**" in line:
                    # Collect elements from following bullet points
                    idx = self.lines.index(line)
                    for j in range(idx + 1, min(idx + 10, len(self.lines))):
                        if self.lines[j].strip().startswith("-"):
                            element = self.lines[j].strip()[1:].strip()
                            current_direction.key_elements.append(element)
                        elif self.lines[j].startswith("###") or self.lines[j].startswith("##"):
                            break

        return directions
