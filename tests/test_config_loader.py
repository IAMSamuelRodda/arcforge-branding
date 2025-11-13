"""Tests for configuration loader."""

import os
import pytest
from pathlib import Path
from config.loader import ConfigLoader, ConfigError


@pytest.fixture
def config_dir():
    """Path to test config directory."""
    repo_root = Path(__file__).parent.parent
    return repo_root / "config"


@pytest.fixture
def loader(config_dir):
    """Create config loader instance."""
    return ConfigLoader(config_dir)


class TestConfigLoader:
    """Test suite for ConfigLoader."""

    def test_init_default_path(self):
        """Test initialization with default config path."""
        loader = ConfigLoader()
        assert loader.config_dir.exists()
        assert loader.config_dir.name == "config"

    def test_init_custom_path(self, config_dir):
        """Test initialization with custom config path."""
        loader = ConfigLoader(config_dir)
        assert loader.config_dir == config_dir

    def test_init_invalid_path(self):
        """Test initialization with invalid path raises error."""
        with pytest.raises(ConfigError, match="Configuration directory not found"):
            ConfigLoader(Path("/nonexistent/path"))

    def test_load_models_config(self, loader):
        """Test loading models configuration."""
        config = loader.load_models_config()

        assert "version" in config
        assert "models" in config
        assert "generation_strategy" in config
        assert "budget" in config

    def test_load_brand_criteria(self, loader):
        """Test loading brand criteria configuration."""
        config = loader.load_brand_criteria()

        assert "version" in config
        assert "color_accuracy" in config
        assert "aesthetic_quality" in config
        assert "composition" in config
        assert "quality_gates" in config

    def test_load_scoring_weights(self, loader):
        """Test loading scoring weights configuration."""
        config = loader.load_scoring_weights()

        assert "version" in config
        assert "default" in config
        assert "components" in config
        assert "layouts" in config
        assert "code" in config

    def test_load_nonexistent_file(self, loader):
        """Test loading nonexistent file raises error."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            loader.load("nonexistent.yaml")

    def test_env_var_substitution(self, loader):
        """Test environment variable substitution."""
        # Set test environment variable
        os.environ["TEST_API_KEY"] = "test_key_12345"

        # Create test YAML with env var
        test_content = "api_key: ${TEST_API_KEY}"
        result = loader._substitute_env_vars(test_content)

        assert "test_key_12345" in result
        assert "${TEST_API_KEY}" not in result

        # Cleanup
        del os.environ["TEST_API_KEY"]

    def test_env_var_not_set(self, loader):
        """Test that unset environment variables are left as-is."""
        test_content = "api_key: ${UNSET_VAR}"
        result = loader._substitute_env_vars(test_content)

        # Should leave unset variables as-is
        assert "${UNSET_VAR}" in result

    def test_validate_api_keys(self, loader):
        """Test API key validation."""
        # Save original environment
        original_env = os.environ.copy()

        try:
            # Clear API keys
            for key in ["REPLICATE_API_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                os.environ.pop(key, None)

            validation = loader.validate_api_keys()

            assert "REPLICATE_API_TOKEN" in validation
            assert "OPENAI_API_KEY" in validation
            assert "ANTHROPIC_API_KEY" in validation
            assert all(v == False for v in validation.values())

            # Set one key
            os.environ["REPLICATE_API_TOKEN"] = "test_key"
            validation = loader.validate_api_keys()
            assert validation["REPLICATE_API_TOKEN"] == True

        finally:
            # Restore environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_env_var(self, loader):
        """Test getting environment variable."""
        os.environ["TEST_VAR"] = "test_value"

        assert loader.get_env_var("TEST_VAR") == "test_value"
        assert loader.get_env_var("NONEXISTENT") is None
        assert loader.get_env_var("NONEXISTENT", "default") == "default"

        del os.environ["TEST_VAR"]

    def test_set_env_var(self, loader):
        """Test setting environment variable."""
        loader.set_env_var("TEST_SET_VAR", "test_value")

        assert os.environ["TEST_SET_VAR"] == "test_value"

        del os.environ["TEST_SET_VAR"]

    def test_validate_models_config(self, loader):
        """Test models configuration validation."""
        assert loader.validate_config("models") == True

    def test_validate_brand_criteria_config(self, loader):
        """Test brand criteria configuration validation."""
        assert loader.validate_config("brand-criteria") == True

    def test_validate_scoring_weights_config(self, loader):
        """Test scoring weights configuration validation."""
        assert loader.validate_config("scoring-weights") == True


class TestModelsConfig:
    """Test suite for models configuration structure."""

    def test_models_section_exists(self, loader):
        """Test that models section exists with valid structure."""
        config = loader.load_models_config()

        assert "models" in config
        assert isinstance(config["models"], dict)
        assert len(config["models"]) > 0

    def test_stable_diffusion_config(self, loader):
        """Test Stable Diffusion model configuration."""
        config = loader.load_models_config()
        sd = config["models"]["stable_diffusion"]

        assert sd["enabled"] == True
        assert sd["provider"] == "replicate"
        assert "model_id" in sd
        assert "api_key" in sd
        assert "parameters" in sd
        assert "rate_limiting" in sd
        assert "cost_per_generation" in sd

    def test_generation_strategy(self, loader):
        """Test generation strategy configuration."""
        config = loader.load_models_config()
        strategy = config["generation_strategy"]

        assert "primary_model" in strategy
        assert "fallback_models" in strategy
        assert "retry" in strategy

    def test_budget_config(self, loader):
        """Test budget configuration."""
        config = loader.load_models_config()
        budget = config["budget"]

        assert "monthly_limit_usd" in budget
        assert budget["monthly_limit_usd"] == 60.0
        assert "alert_thresholds" in budget
        assert len(budget["alert_thresholds"]) >= 3


class TestBrandCriteriaConfig:
    """Test suite for brand criteria configuration structure."""

    def test_color_accuracy_config(self, loader):
        """Test color accuracy configuration."""
        config = loader.load_brand_criteria()
        color = config["color_accuracy"]

        assert "color_matching" in color
        assert "presence" in color
        assert "target_accuracy" in color
        assert color["target_accuracy"] == 95.0

    def test_aesthetic_quality_config(self, loader):
        """Test aesthetic quality configuration."""
        config = loader.load_brand_criteria()
        aesthetic = config["aesthetic_quality"]

        assert "min_score" in aesthetic
        assert "target_score" in aesthetic
        assert "dimensions" in aesthetic

    def test_quality_gates_config(self, loader):
        """Test quality gates configuration."""
        config = loader.load_brand_criteria()
        gates = config["quality_gates"]

        assert "gate_1_initial" in gates
        assert "gate_2_basic" in gates
        assert "gate_3_brand" in gates
        assert "gate_4_production" in gates


class TestScoringWeightsConfig:
    """Test suite for scoring weights configuration structure."""

    def test_default_weights(self, loader):
        """Test default scoring weights."""
        config = loader.load_scoring_weights()
        default = config["default"]

        assert "dimensions" in default
        assert "composite" in default

        # Check dimension weights
        dims = default["dimensions"]
        assert "clip_similarity" in dims
        assert "color_adherence" in dims
        assert "aesthetic_quality" in dims
        assert "composition" in dims

    def test_weights_sum_to_one(self, loader):
        """Test that default dimension weights sum to 1.0."""
        config = loader.load_scoring_weights()
        dims = config["default"]["dimensions"]

        total_weight = sum(dim["weight"] for dim in dims.values())

        assert 0.99 <= total_weight <= 1.01, f"Weights sum to {total_weight}, expected 1.0"

    def test_component_weights(self, loader):
        """Test component-specific weights."""
        config = loader.load_scoring_weights()
        components = config["components"]

        assert "dimensions" in components
        assert "accessibility" in components["dimensions"]
        assert components["dimensions"]["accessibility"]["weight"] == 0.35

    def test_code_weights(self, loader):
        """Test code export weights."""
        config = loader.load_scoring_weights()
        code = config["code"]

        assert "dimensions" in code
        assert "code_quality" in code["dimensions"]
        assert "performance" in code["dimensions"]
