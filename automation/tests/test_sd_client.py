"""Tests for Stable Diffusion API client."""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from generation.sd_client import (
    StableDiffusionClient,
    GenerationRequest,
    GenerationResult,
    GenerationStats,
    CostTracker,
)


@pytest.fixture
def api_token():
    """Mock API token."""
    return "r8_test_token_12345"


@pytest.fixture
def mock_image_bytes():
    """Create mock image bytes."""
    from PIL import Image
    from io import BytesIO

    img = Image.new("RGB", (512, 512), color=(100, 150, 200))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


class TestCostTracker:
    """Test suite for CostTracker."""

    def test_initialization(self):
        """Test cost tracker initialization."""
        tracker = CostTracker(budget_limit=50.0)

        assert tracker.budget_limit == 50.0
        assert tracker.session_cost == 0.0
        assert tracker.total_cost == 0.0
        assert tracker.generation_count == 0

    def test_add_generation_success(self):
        """Test recording successful generation."""
        tracker = CostTracker()
        tracker.add_generation(0.003, success=True)

        assert tracker.session_cost == 0.003
        assert tracker.total_cost == 0.003
        assert tracker.generation_count == 1
        assert len(tracker.cost_history) == 1

    def test_add_generation_failure(self):
        """Test recording failed generation."""
        tracker = CostTracker()
        tracker.add_generation(0.0, success=False)

        assert tracker.session_cost == 0.0
        assert tracker.total_cost == 0.0
        assert tracker.generation_count == 0  # Failed don't count
        assert len(tracker.cost_history) == 1  # But recorded in history

    def test_check_budget_within_limit(self):
        """Test budget check when within limit."""
        tracker = CostTracker(budget_limit=10.0)
        tracker.add_generation(2.0, success=True)

        check = tracker.check_budget(planned_generations=1000, cost_per_generation=0.003)

        assert check["within_budget"] is True
        assert check["planned_cost"] == 3.0
        assert check["remaining_budget"] == 8.0

    def test_check_budget_exceeds_limit(self):
        """Test budget check when exceeding limit."""
        tracker = CostTracker(budget_limit=5.0)
        tracker.add_generation(4.0, success=True)

        check = tracker.check_budget(planned_generations=1000, cost_per_generation=0.003)

        assert check["within_budget"] is False
        assert check["planned_cost"] == 3.0
        assert check["remaining_budget"] == 1.0

    def test_should_alert(self):
        """Test budget alert threshold."""
        tracker = CostTracker(budget_limit=10.0)

        # Below threshold
        tracker.add_generation(5.0, success=True)
        assert tracker.should_alert(threshold=0.8) is False

        # Above threshold
        tracker.add_generation(4.0, success=True)
        assert tracker.should_alert(threshold=0.8) is True

    def test_get_summary(self):
        """Test cost summary."""
        tracker = CostTracker(budget_limit=100.0)
        tracker.add_generation(0.003, success=True)
        tracker.add_generation(0.003, success=True)

        summary = tracker.get_summary()

        assert summary["total_cost"] == 0.006
        assert summary["generation_count"] == 2
        assert summary["avg_cost_per_image"] == 0.003
        assert summary["budget_remaining"] == 99.994

    def test_export_history(self, tmp_path):
        """Test exporting cost history."""
        tracker = CostTracker()
        tracker.add_generation(0.003, success=True)

        output_file = tmp_path / "cost_history.json"
        tracker.export_history(output_file)

        assert output_file.exists()

        import json

        with open(output_file, "r") as f:
            data = json.load(f)
            assert "summary" in data
            assert "history" in data
            assert len(data["history"]) == 1


class TestStableDiffusionClient:
    """Test suite for StableDiffusionClient."""

    def test_initialization_with_token(self, api_token):
        """Test client initialization with API token."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        assert client.api_token == api_token
        assert client.model == "flux"
        assert client.model_config["cost"] == 0.003
        assert client.max_concurrent == 50

    def test_initialization_without_token(self):
        """Test client requires API token."""
        with pytest.raises(ValueError, match="Replicate API token required"):
            StableDiffusionClient(api_token=None)

    def test_initialization_with_env_token(self, api_token, monkeypatch):
        """Test client initialization from environment variable."""
        monkeypatch.setenv("REPLICATE_API_TOKEN", api_token)
        client = StableDiffusionClient(model="flux")

        assert client.api_token == api_token

    def test_initialization_unknown_model(self, api_token):
        """Test initialization with unknown model."""
        with pytest.raises(ValueError, match="Unknown model"):
            StableDiffusionClient(api_token=api_token, model="unknown")

    def test_model_configs(self, api_token):
        """Test model configurations."""
        client_flux = StableDiffusionClient(api_token=api_token, model="flux")
        assert client_flux.model_config["cost"] == 0.003

        client_sd35 = StableDiffusionClient(api_token=api_token, model="sd35")
        assert client_sd35.model_config["cost"] == 0.035

    @pytest.mark.asyncio
    async def test_generate_success(self, api_token, mock_image_bytes):
        """Test successful image generation."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        # Mock Replicate API
        with patch.object(client.client, "run", return_value=["https://example.com/image.png"]):
            # Mock image download
            client._download_image = AsyncMock(return_value=mock_image_bytes)

            result = await client.generate("A test prompt")

            assert result.success is True
            assert result.prompt_text == "A test prompt"
            assert result.image_bytes == mock_image_bytes
            assert result.cost == 0.003
            assert result.error is None

    @pytest.mark.asyncio
    async def test_generate_with_prompt_id(self, api_token, mock_image_bytes):
        """Test generation with custom prompt ID."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        with patch.object(client.client, "run", return_value=["https://example.com/image.png"]):
            client._download_image = AsyncMock(return_value=mock_image_bytes)

            result = await client.generate("A test prompt", prompt_id="custom_id_123")

            assert result.success is True
            assert result.prompt_id == "custom_id_123"

    @pytest.mark.asyncio
    async def test_generate_failure(self, api_token):
        """Test handling generation failure."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        # Mock API failure
        with patch.object(client.client, "run", side_effect=Exception("API Error")):
            result = await client.generate("A test prompt")

            assert result.success is False
            assert result.error == "API Error"
            assert result.image_bytes is None

    @pytest.mark.asyncio
    async def test_generate_batch(self, api_token, mock_image_bytes):
        """Test batch generation."""
        client = StableDiffusionClient(api_token=api_token, model="flux", max_concurrent=10)

        requests = [
            GenerationRequest(prompt_id=f"id_{i}", prompt_text=f"Prompt {i}")
            for i in range(5)
        ]

        # Mock Replicate API
        with patch.object(client.client, "run", return_value=["https://example.com/image.png"]):
            client._download_image = AsyncMock(return_value=mock_image_bytes)

            results, stats = await client.generate_batch(requests, show_progress=False)

            assert len(results) == 5
            assert stats.total_requests == 5
            assert stats.successful == 5
            assert stats.failed == 0
            assert stats.total_cost == 0.015  # 5 * 0.003

    @pytest.mark.asyncio
    async def test_generate_batch_with_failures(self, api_token, mock_image_bytes):
        """Test batch generation with some failures."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        requests = [
            GenerationRequest(prompt_id=f"id_{i}", prompt_text=f"Prompt {i}")
            for i in range(5)
        ]

        # Mock API: fail on odd indices
        def mock_run(*args, **kwargs):
            prompt = kwargs.get("input", {}).get("prompt", "")
            if "1" in prompt or "3" in prompt:
                raise Exception("API Error")
            return ["https://example.com/image.png"]

        with patch.object(client.client, "run", side_effect=mock_run):
            client._download_image = AsyncMock(return_value=mock_image_bytes)

            results, stats = await client.generate_batch(requests, show_progress=False)

            assert len(results) == 5
            assert stats.successful == 3
            assert stats.failed == 2
            assert abs(stats.total_cost - 0.009) < 0.0001  # 3 successful * 0.003, allow for floating point

    @pytest.mark.asyncio
    async def test_generate_batch_budget_check(self, api_token, mock_image_bytes, monkeypatch):
        """Test batch generation budget checking."""
        client = StableDiffusionClient(api_token=api_token, model="flux", budget_limit=0.01)

        # Use up most of budget
        client.cost_tracker.add_generation(0.008, success=True)

        requests = [
            GenerationRequest(prompt_id=f"id_{i}", prompt_text=f"Prompt {i}")
            for i in range(5)  # Would cost 0.015, exceeding budget
        ]

        # Mock user input to cancel
        monkeypatch.setattr("builtins.input", lambda _: "n")

        with patch.object(client.client, "run", return_value=["https://example.com/image.png"]):
            client._download_image = AsyncMock(return_value=mock_image_bytes)

            results, stats = await client.generate_batch(requests, show_progress=False)

            # Should be cancelled, no results
            assert len(results) == 0
            assert stats.total_requests == 0

    @pytest.mark.asyncio
    async def test_download_image(self, api_token):
        """Test image download."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.content = b"fake_image_bytes"
        mock_response.raise_for_status = MagicMock()

        client.http_client.get = AsyncMock(return_value=mock_response)

        image_bytes = await client._download_image("https://example.com/image.png")

        assert image_bytes == b"fake_image_bytes"

    def test_generate_prompt_id(self, api_token):
        """Test prompt ID generation."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        prompt_id = client._generate_prompt_id("A test prompt")

        assert len(prompt_id) == 16  # MD5 hash truncated to 16 chars
        assert isinstance(prompt_id, str)

        # Same prompt should generate same ID
        prompt_id2 = client._generate_prompt_id("A test prompt")
        assert prompt_id == prompt_id2

    def test_save_image(self, api_token, mock_image_bytes, tmp_path):
        """Test saving generated image."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        result = GenerationResult(
            prompt_id="test_id",
            prompt_text="Test prompt",
            image_bytes=mock_image_bytes,
            success=True,
        )

        output_path = tmp_path / "images" / "test.png"
        client.save_image(result, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_image_failure(self, api_token):
        """Test saving failed generation raises error."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        result = GenerationResult(
            prompt_id="test_id",
            prompt_text="Test prompt",
            success=False,
            error="Generation failed",
        )

        with pytest.raises(ValueError, match="Cannot save failed generation"):
            client.save_image(result, Path("test.png"))

    def test_get_cost_summary(self, api_token):
        """Test getting cost summary."""
        client = StableDiffusionClient(api_token=api_token, model="flux", budget_limit=10.0)

        client.cost_tracker.add_generation(0.003, success=True)
        client.cost_tracker.add_generation(0.003, success=True)

        summary = client.get_cost_summary()

        assert summary["total_cost"] == 0.006
        assert summary["generation_count"] == 2
        assert summary["budget_remaining"] == 9.994

    def test_export_cost_history(self, api_token, tmp_path):
        """Test exporting cost history."""
        client = StableDiffusionClient(api_token=api_token, model="flux")

        client.cost_tracker.add_generation(0.003, success=True)

        output_path = tmp_path / "cost_history.json"
        client.export_cost_history(output_path)

        assert output_path.exists()

    @pytest.mark.asyncio
    async def test_context_manager(self, api_token):
        """Test async context manager."""
        async with StableDiffusionClient(api_token=api_token, model="flux") as client:
            assert client.api_token == api_token

        # HTTP client should be closed
        assert client.http_client.is_closed


class TestGenerationRequest:
    """Test GenerationRequest dataclass."""

    def test_creation(self):
        """Test creating a generation request."""
        request = GenerationRequest(
            prompt_id="test_id",
            prompt_text="A beautiful landscape",
            parameters={"width": 1024, "height": 1024},
            model_format="flux",
        )

        assert request.prompt_id == "test_id"
        assert request.prompt_text == "A beautiful landscape"
        assert request.parameters == {"width": 1024, "height": 1024}
        assert request.model_format == "flux"

    def test_default_values(self):
        """Test default parameter values."""
        request = GenerationRequest(prompt_id="id", prompt_text="Test")

        assert request.parameters == {}
        assert request.model_format == "flux"


class TestGenerationResult:
    """Test GenerationResult dataclass."""

    def test_creation_success(self):
        """Test creating a successful result."""
        result = GenerationResult(
            prompt_id="test_id",
            prompt_text="Test prompt",
            image_url="https://example.com/image.png",
            image_bytes=b"fake_bytes",
            generation_time=2.5,
            cost=0.003,
            success=True,
        )

        assert result.success is True
        assert result.prompt_text == "Test prompt"
        assert result.cost == 0.003
        assert result.error is None

    def test_creation_failure(self):
        """Test creating a failed result."""
        result = GenerationResult(
            prompt_id="test_id",
            prompt_text="Test prompt",
            error="API timeout",
            success=False,
        )

        assert result.success is False
        assert result.error == "API timeout"
        assert result.image_bytes is None
        assert result.cost == 0.003  # Default cost


class TestGenerationStats:
    """Test GenerationStats dataclass."""

    def test_creation(self):
        """Test creating generation stats."""
        stats = GenerationStats(
            total_requests=100,
            successful=95,
            failed=5,
            total_cost=0.285,
            total_time=150.0,
            avg_generation_time=1.5,
        )

        assert stats.total_requests == 100
        assert stats.successful == 95
        assert stats.failed == 5
        assert stats.total_cost == 0.285
        assert stats.avg_generation_time == 1.5

    def test_default_values(self):
        """Test default stat values."""
        stats = GenerationStats()

        assert stats.total_requests == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.total_cost == 0.0
