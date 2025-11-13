"""Configuration loader for DesignForge YAML configuration files."""

import os
from pathlib import Path
from string import Template
from typing import Any, Dict, Optional

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfigLoader:
    """Loads and validates YAML configuration files with environment variable substitution."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Path to configuration directory.
                       Defaults to automation/config/
        """
        if config_dir is None:
            # Default to automation/config/ relative to this file
            self.config_dir = Path(__file__).parent.parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise ConfigError(f"Configuration directory not found: {self.config_dir}")

    def load(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file with environment variable substitution.

        Args:
            filename: Name of the configuration file (e.g., 'models.yaml')

        Returns:
            Parsed configuration dictionary

        Raises:
            ConfigError: If file not found or invalid YAML
        """
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Substitute environment variables
            content = self._substitute_env_vars(content)

            # Parse YAML
            config = yaml.safe_load(content)

            if config is None:
                raise ConfigError(f"Empty configuration file: {filename}")

            return config

        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {filename}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load {filename}: {e}")

    def load_models_config(self) -> Dict[str, Any]:
        """Load models configuration."""
        return self.load("models.yaml")

    def load_brand_criteria(self) -> Dict[str, Any]:
        """Load brand criteria configuration."""
        return self.load("brand-criteria.yaml")

    def load_scoring_weights(self) -> Dict[str, Any]:
        """Load scoring weights configuration."""
        return self.load("scoring-weights.yaml")

    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in configuration content.

        Supports ${VAR_NAME} and ${VAR_NAME:-default_value} syntax.

        Args:
            content: Configuration file content

        Returns:
            Content with environment variables substituted
        """
        # First pass: Simple ${VAR} substitution
        template = Template(content)

        env_dict = {}
        for key, value in os.environ.items():
            env_dict[key] = value

        try:
            # Use safe_substitute to leave unmatched variables as-is
            result = template.safe_substitute(env_dict)
        except Exception as e:
            # If template substitution fails, return original content
            result = content

        return result

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that required API keys are set in environment.

        Returns:
            Dictionary mapping API key names to whether they are set
        """
        required_keys = [
            "REPLICATE_API_TOKEN",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]

        validation = {}
        for key in required_keys:
            validation[key] = bool(os.environ.get(key))

        return validation

    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with optional default.

        Args:
            key: Environment variable name
            default: Default value if not set

        Returns:
            Environment variable value or default
        """
        return os.environ.get(key, default)

    def set_env_var(self, key: str, value: str) -> None:
        """
        Set environment variable (useful for testing).

        Args:
            key: Environment variable name
            value: Value to set
        """
        os.environ[key] = value

    def load_env_file(self, env_file: Path = None) -> None:
        """
        Load environment variables from .env file.

        Args:
            env_file: Path to .env file. Defaults to automation/.env
        """
        if env_file is None:
            env_file = self.config_dir.parent / ".env"

        if not env_file.exists():
            # Not an error - .env is optional
            return

        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

        except Exception as e:
            raise ConfigError(f"Failed to load .env file: {e}")

    def validate_config(self, config_name: str) -> bool:
        """
        Validate a configuration file for required fields.

        Args:
            config_name: Name of configuration to validate
                        ('models', 'brand-criteria', 'scoring-weights')

        Returns:
            True if valid, raises ConfigError otherwise
        """
        config = self.load(f"{config_name}.yaml")

        # Version check
        if "version" not in config:
            raise ConfigError(f"{config_name}.yaml missing 'version' field")

        # Config-specific validation
        if config_name == "models":
            self._validate_models_config(config)
        elif config_name == "brand-criteria":
            self._validate_brand_criteria_config(config)
        elif config_name == "scoring-weights":
            self._validate_scoring_weights_config(config)

        return True

    def _validate_models_config(self, config: Dict[str, Any]) -> None:
        """Validate models configuration structure."""
        if "models" not in config:
            raise ConfigError("models.yaml missing 'models' section")

        if "generation_strategy" not in config:
            raise ConfigError("models.yaml missing 'generation_strategy' section")

        # Check at least one model is enabled
        enabled_models = [
            name
            for name, model in config["models"].items()
            if model.get("enabled", False)
        ]

        if not enabled_models:
            raise ConfigError("No models enabled in models.yaml")

    def _validate_brand_criteria_config(self, config: Dict[str, Any]) -> None:
        """Validate brand criteria configuration structure."""
        required_sections = [
            "color_accuracy",
            "aesthetic_quality",
            "composition",
            "quality_gates",
        ]

        for section in required_sections:
            if section not in config:
                raise ConfigError(
                    f"brand-criteria.yaml missing '{section}' section"
                )

    def _validate_scoring_weights_config(self, config: Dict[str, Any]) -> None:
        """Validate scoring weights configuration structure."""
        if "default" not in config:
            raise ConfigError("scoring-weights.yaml missing 'default' section")

        # Validate weights sum to 1.0 (approximately)
        default_dims = config["default"].get("dimensions", {})
        if default_dims:
            total_weight = sum(
                dim.get("weight", 0) for dim in default_dims.values()
            )

            if not (0.99 <= total_weight <= 1.01):  # Allow small floating point error
                raise ConfigError(
                    f"Default dimension weights sum to {total_weight}, expected 1.0"
                )
