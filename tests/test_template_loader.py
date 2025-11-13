"""Tests for prompt template loader."""

import pytest
from pathlib import Path
from design_assets.template_loader import (
    PromptTemplateLoader,
    PromptTemplate,
    PromptTemplateCollection,
)


@pytest.fixture
def prompt_template_path():
    """Path to the actual Midjourney prompts file."""
    # Get repo root (two levels up from tests/)
    repo_root = Path(__file__).parent.parent
    return repo_root / "archives" / "case-study-arcforge" / "design" / "MIDJOURNEY-PROMPTS-V2-ANVIL.md"


@pytest.fixture
def loader(prompt_template_path):
    """Create loader instance."""
    return PromptTemplateLoader(prompt_template_path)


@pytest.fixture
def collection(loader):
    """Load prompt template collection."""
    return loader.load()


class TestPromptTemplateLoader:
    """Test suite for PromptTemplateLoader."""

    def test_loader_initialization(self, prompt_template_path):
        """Test loader can be initialized with valid path."""
        loader = PromptTemplateLoader(prompt_template_path)
        assert loader.template_path == prompt_template_path
        assert loader.content
        assert loader.lines

    def test_loader_invalid_path(self):
        """Test loader raises error with invalid path."""
        with pytest.raises(FileNotFoundError):
            PromptTemplateLoader(Path("nonexistent.md"))

    def test_load_returns_collection(self, collection):
        """Test load() returns PromptTemplateCollection."""
        assert isinstance(collection, PromptTemplateCollection)
        assert collection.source_file is not None

    def test_collection_has_templates(self, collection):
        """Test collection contains templates."""
        assert len(collection.templates) > 0
        assert all(isinstance(t, PromptTemplate) for t in collection.templates)

    def test_collection_has_title(self, collection):
        """Test collection extracts title from file."""
        assert collection.title is not None
        assert len(collection.title) > 0

    def test_template_has_text(self, collection):
        """Test templates have prompt text."""
        for template in collection.templates:
            assert template.text
            assert len(template.text) >= 10  # Minimum reasonable length

    def test_template_extracts_parameters(self, collection):
        """Test templates extract Midjourney parameters."""
        # At least some templates should have parameters
        templates_with_params = [t for t in collection.templates if t.parameters]
        assert len(templates_with_params) > 0

        # Check for common Midjourney parameters
        all_params = {}
        for t in templates_with_params:
            all_params.update(t.parameters)

        # Should find --v (version) and --s (stylization)
        assert "--v" in all_params or "--s" in all_params

    def test_template_classifies_categories(self, collection):
        """Test templates are classified into categories."""
        categories = [t.category for t in collection.templates]
        assert len(categories) > 0

        # For the anvil logo prompts, should be mostly "logo"
        logo_count = categories.count("logo")
        assert logo_count > 0

    def test_template_extracts_keywords(self, collection):
        """Test templates extract style keywords."""
        # At least some templates should have keywords
        templates_with_keywords = [t for t in collection.templates if t.keywords]
        assert len(templates_with_keywords) > 0

        # Check for expected keywords in the anvil prompts
        all_keywords = []
        for t in collection.templates:
            all_keywords.extend(t.keywords)

        # Should find common style keywords
        assert (
            "minimalist" in all_keywords
            or "vector" in all_keywords
            or "isometric" in all_keywords
            or "geometric" in all_keywords
        )

    def test_template_finds_names(self, collection):
        """Test templates find names from headings."""
        # At least some templates should have names
        templates_with_names = [t for t in collection.templates if t.name]
        assert len(templates_with_names) > 0

    def test_substitute_variables_basic(self, loader):
        """Test variable substitution with basic template."""
        template = PromptTemplate(
            text="A {style} logo with {color} accents",
            variables={"style", "color"},
        )

        result = loader.substitute_variables(
            template, {"style": "minimalist", "color": "blue"}
        )

        assert result == "A minimalist logo with blue accents"
        assert "{style}" not in result
        assert "{color}" not in result

    def test_substitute_variables_partial(self, loader):
        """Test variable substitution with missing variables."""
        template = PromptTemplate(
            text="A {style} logo with {color} accents and {feature} elements",
            variables={"style", "color", "feature"},
        )

        result = loader.substitute_variables(template, {"style": "modern", "color": "red"})

        assert result == "A modern logo with red accents and {feature} elements"
        assert "{style}" not in result
        assert "{color}" not in result
        assert "{feature}" in result  # Unsubstituted

    def test_substitute_variables_empty(self, loader):
        """Test variable substitution with no variables."""
        template = PromptTemplate(
            text="A simple logo with no variables",
            variables=set(),
        )

        result = loader.substitute_variables(template, {"style": "unused"})

        assert result == "A simple logo with no variables"

    def test_code_block_pattern(self, loader):
        """Test code block regex pattern."""
        test_content = """
# Test

Some text

```
prompt content here
with multiple lines
```

More text

```
another prompt
```
"""
        matches = loader.CODE_BLOCK_PATTERN.findall(test_content)
        assert len(matches) == 2
        assert "prompt content here" in matches[0]
        assert "another prompt" in matches[1]

    def test_variable_pattern(self, loader):
        """Test variable detection regex pattern."""
        test_text = "A {style} logo with {color_scheme} and {size} parameters"
        variables = loader.VARIABLE_PATTERN.findall(test_text)

        assert len(variables) == 3
        assert "style" in variables
        assert "color_scheme" in variables
        assert "size" in variables

    def test_parameter_pattern(self, loader):
        """Test Midjourney parameter regex pattern."""
        test_text = "minimalist logo --v 6 --s 250 --style raw --ar 1:1"
        parameters = dict(loader.PARAMETER_PATTERN.findall(test_text))

        assert len(parameters) >= 3
        assert parameters["--v"] == "6"
        assert parameters["--s"] == "250"
        assert parameters["--style"] == "raw"

    def test_load_directory(self, tmp_path):
        """Test loading multiple template files from directory."""
        # Create test template files
        test_file1 = tmp_path / "PROMPT-TEMPLATES-1.md"
        test_file1.write_text(
            """# Test Templates 1

```
A {style} logo with clean lines --v 6
```
"""
        )

        test_file2 = tmp_path / "MIDJOURNEY-PROMPTS-TEST.md"
        test_file2.write_text(
            """# Test Templates 2

```
Another {type} design with {color} palette --s 250
```
"""
        )

        # Load all templates from directory
        collections = PromptTemplateLoader.load_directory(tmp_path)

        assert len(collections) == 2
        assert all(isinstance(c, PromptTemplateCollection) for c in collections)
        assert sum(len(c.templates) for c in collections) == 2

    def test_load_directory_invalid_path(self):
        """Test load_directory with invalid path."""
        with pytest.raises(NotADirectoryError):
            PromptTemplateLoader.load_directory(Path("nonexistent_directory"))

    def test_load_directory_empty(self, tmp_path):
        """Test load_directory with directory containing no template files."""
        # Create non-template file
        (tmp_path / "README.md").write_text("Not a template")

        collections = PromptTemplateLoader.load_directory(tmp_path)
        assert len(collections) == 0


class TestPromptTemplate:
    """Test PromptTemplate dataclass."""

    def test_template_creation_minimal(self):
        """Test creating PromptTemplate with required fields only."""
        template = PromptTemplate(text="A simple prompt")
        assert template.text == "A simple prompt"
        assert template.variables == set()
        assert template.name is None
        assert template.category is None
        assert template.keywords == []
        assert template.parameters == {}

    def test_template_creation_complete(self):
        """Test creating PromptTemplate with all fields."""
        template = PromptTemplate(
            text="A {style} logo --v 6",
            variables={"style"},
            name="Test Template",
            category="logo",
            keywords=["minimalist", "vector"],
            parameters={"--v": "6"},
        )
        assert template.text == "A {style} logo --v 6"
        assert template.variables == {"style"}
        assert template.name == "Test Template"
        assert template.category == "logo"
        assert len(template.keywords) == 2
        assert template.parameters["--v"] == "6"


class TestPromptTemplateCollection:
    """Test PromptTemplateCollection dataclass."""

    def test_collection_creation_empty(self):
        """Test creating empty PromptTemplateCollection."""
        collection = PromptTemplateCollection()
        assert collection.templates == []
        assert collection.source_file is None
        assert collection.title is None
        assert collection.description is None

    def test_collection_creation_with_data(self):
        """Test creating PromptTemplateCollection with data."""
        template1 = PromptTemplate(text="Prompt 1")
        template2 = PromptTemplate(text="Prompt 2")

        collection = PromptTemplateCollection(
            templates=[template1, template2],
            source_file=Path("test.md"),
            title="Test Collection",
            description="A test collection",
        )

        assert len(collection.templates) == 2
        assert collection.source_file == Path("test.md")
        assert collection.title == "Test Collection"
        assert collection.description == "A test collection"


class TestRegexPatterns:
    """Test regex pattern edge cases."""

    def test_variable_pattern_edge_cases(self):
        """Test variable pattern with various edge cases."""
        pattern = PromptTemplateLoader.VARIABLE_PATTERN

        # Valid variables
        assert pattern.findall("{valid_name}") == ["valid_name"]
        assert pattern.findall("{CamelCase}") == ["CamelCase"]
        assert pattern.findall("{name123}") == ["name123"]
        assert pattern.findall("{_private}") == ["_private"]

        # Invalid variables (should not match)
        assert pattern.findall("{123invalid}") == []  # Starts with number
        assert pattern.findall("{invalid-name}") == []  # Contains hyphen

        # Multiple variables
        result = pattern.findall("{var1} and {var2} and {var3}")
        assert result == ["var1", "var2", "var3"]

    def test_parameter_pattern_edge_cases(self):
        """Test parameter pattern with various formats."""
        pattern = PromptTemplateLoader.PARAMETER_PATTERN

        # Standard format
        assert dict(pattern.findall("--v 6 --s 250")) == {"--v": "6", "--s": "250"}

        # Different value types
        params = dict(pattern.findall("--style raw --ar 16:9 --q 2"))
        assert "--style" in params
        assert "--ar" in params

        # Should not match incomplete patterns
        assert pattern.findall("-- value") == []  # No parameter name
        assert pattern.findall("--param") == []  # No value

    def test_code_block_pattern_edge_cases(self):
        """Test code block pattern with various formats."""
        pattern = PromptTemplateLoader.CODE_BLOCK_PATTERN

        # Standard code block
        matches = pattern.findall("```\ncode here\n```")
        assert len(matches) == 1
        assert "code here" in matches[0]

        # Code block without newlines
        matches = pattern.findall("```code here```")
        assert len(matches) == 1

        # Multiple code blocks
        text = "```\nblock1\n```\ntext\n```\nblock2\n```"
        matches = pattern.findall(text)
        assert len(matches) == 2

        # Empty code block
        matches = pattern.findall("```\n```")
        assert len(matches) == 1
        assert matches[0].strip() == ""
