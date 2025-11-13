"""Tests for multi-backend generation system."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

import pytest

from generation.backends import (
    GenerationBackend,
    LocalGPUBackend,
    ReplicateBackend,
    BackendConfig,
)
from generation.multi_backend_client import MultiBackendClient, BackendStats
from generation.sd_client import GenerationRequest


# Mock backends for testing


class MockSuccessBackend(GenerationBackend):
    """Mock backend that always succeeds."""

    def __init__(self, name: str = "mock-success", cost: float = 0.001):
        config = BackendConfig(name=name, cost_per_image=cost)
        super().__init__(config)
        self.generation_count = 0

    async def generate(self, prompt: str, width: int = 512, height: int = 512, **params):
        self.generation_count += 1
        # Return fake image bytes
        return b"fake_image_data", 1.5

    async def is_available(self) -> bool:
        return True


class MockFailBackend(GenerationBackend):
    """Mock backend that always fails."""

    def __init__(self, name: str = "mock-fail"):
        config = BackendConfig(name=name, cost_per_image=0.0)
        super().__init__(config)

    async def generate(self, prompt: str, width: int = 512, height: int = 512, **params):
        raise Exception("Mock generation failure")

    async def is_available(self) -> bool:
        return True


class MockUnavailableBackend(GenerationBackend):
    """Mock backend that is unavailable."""

    def __init__(self, name: str = "mock-unavailable"):
        config = BackendConfig(name=name, cost_per_image=0.0)
        super().__init__(config)

    async def generate(self, prompt: str, width: int = 512, height: int = 512, **params):
        return b"fake_image_data", 1.0

    async def is_available(self) -> bool:
        return False


# Fixtures


@pytest.fixture
def mock_image_bytes():
    """Create mock image bytes."""
    from PIL import Image
    from io import BytesIO

    img = Image.new("RGB", (512, 512), color=(100, 150, 200))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# Backend Tests


class TestBackendConfig:
    """Test BackendConfig dataclass."""

    def test_initialization(self):
        """Test backend config creation."""
        config = BackendConfig(
            name="test-backend",
            enabled=True,
            cost_per_image=0.003,
            timeout=30.0,
        )

        assert config.name == "test-backend"
        assert config.enabled is True
        assert config.cost_per_image == 0.003
        assert config.timeout == 30.0

    def test_default_values(self):
        """Test default config values."""
        config = BackendConfig(name="test")

        assert config.enabled is True
        assert config.cost_per_image == 0.0
        assert config.timeout == 30.0


class TestLocalGPUBackend:
    """Test LocalGPUBackend."""

    def test_initialization(self):
        """Test local GPU backend initialization."""
        backend = LocalGPUBackend(
            api_url="http://192.168.1.100:8188",
            model="flux-schnell",
        )

        assert backend.api_url == "http://192.168.1.100:8188"
        assert backend.model == "flux-schnell"
        assert backend.config.cost_per_image == 0.0002  # Electricity estimate

    def test_workflow_building_flux(self):
        """Test Flux workflow generation."""
        backend = LocalGPUBackend(model="flux-schnell")

        workflow = backend._build_flux_workflow(
            "A test prompt", width=1024, height=1024, steps=4, seed=42
        )

        assert "1" in workflow  # CLIPTextEncode node
        assert workflow["1"]["inputs"]["text"] == "A test prompt"
        assert workflow["2"]["inputs"]["width"] == 1024
        assert workflow["3"]["inputs"]["steps"] == 4
        assert workflow["3"]["inputs"]["seed"] == 42

    def test_workflow_building_sd35(self):
        """Test SD 3.5 workflow generation."""
        backend = LocalGPUBackend(model="sd35")

        workflow = backend._build_sd35_workflow(
            "A test prompt", width=1024, height=1024, steps=28, guidance_scale=7.0
        )

        assert "1" in workflow  # Positive prompt
        assert workflow["1"]["inputs"]["text"] == "A test prompt"
        assert workflow["4"]["inputs"]["cfg"] == 7.0
        assert workflow["4"]["inputs"]["steps"] == 28

    @pytest.mark.asyncio
    async def test_is_available_success(self):
        """Test availability check when API is up."""
        backend = LocalGPUBackend(api_url="http://localhost:8188")

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        backend.http_client.get = AsyncMock(return_value=mock_response)

        available = await backend.is_available()
        assert available is True

    @pytest.mark.asyncio
    async def test_is_available_failure(self):
        """Test availability check when API is down."""
        backend = LocalGPUBackend(api_url="http://localhost:8188")

        # Mock failed response
        backend.http_client.get = AsyncMock(side_effect=Exception("Connection refused"))

        available = await backend.is_available()
        assert available is False


class TestReplicateBackend:
    """Test ReplicateBackend."""

    def test_initialization_with_token(self):
        """Test Replicate backend initialization."""
        backend = ReplicateBackend(api_token="r8_test_token", model="flux-schnell")

        assert backend.api_token == "r8_test_token"
        assert backend.model == "flux-schnell"
        assert backend.config.cost_per_image == 0.003

    def test_initialization_without_token(self):
        """Test Replicate backend requires token."""
        with pytest.raises(ValueError, match="Replicate API token required"):
            ReplicateBackend(api_token=None, model="flux-schnell")

    def test_model_configs(self):
        """Test model configuration mapping."""
        backend_flux = ReplicateBackend(api_token="test", model="flux-schnell")
        assert backend_flux.config.cost_per_image == 0.003

        backend_sd35 = ReplicateBackend(api_token="test", model="sd35")
        assert backend_sd35.config.cost_per_image == 0.035

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test Replicate availability check."""
        backend = ReplicateBackend(api_token="test", model="flux-schnell")

        available = await backend.is_available()
        assert available is True  # Token is set


# MultiBackendClient Tests


class TestMultiBackendClient:
    """Test MultiBackendClient."""

    def test_initialization_local_only(self):
        """Test client with only local GPU."""
        # Mock LocalGPUBackend to avoid connection
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_local.return_value = MockSuccessBackend(name="local")

            client = MultiBackendClient(
                local_gpu_enabled=True,
                local_gpu_url="http://localhost:8188",
                replicate_token=None,
            )

            assert "local" in client.backends
            assert len(client.backends) == 1

    def test_initialization_replicate_only(self):
        """Test client with only Replicate."""
        client = MultiBackendClient(
            local_gpu_enabled=False,
            replicate_token="r8_test_token",
        )

        assert "replicate" in client.backends
        assert len(client.backends) == 1

    def test_initialization_both_backends(self):
        """Test client with both backends."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_local.return_value = MockSuccessBackend(name="local")

            client = MultiBackendClient(
                local_gpu_enabled=True,
                local_gpu_url="http://localhost:8188",
                replicate_token="r8_test_token",
            )

            assert "local" in client.backends
            assert "replicate" in client.backends
            assert len(client.backends) == 2

    def test_initialization_no_backends(self):
        """Test client requires at least one backend."""
        with pytest.raises(ValueError, match="No backends available"):
            MultiBackendClient(
                local_gpu_enabled=False,
                replicate_token=None,
            )

    def test_backend_order_prefer_local(self):
        """Test backend order when preferring local."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_local.return_value = MockSuccessBackend(name="local")

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token="r8_test",
                prefer_local=True,
            )

            order = client._get_backend_order()
            assert order[0] == "local"
            assert order[1] == "replicate"

    def test_backend_order_prefer_replicate(self):
        """Test backend order when not preferring local."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_local.return_value = MockSuccessBackend(name="local")

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token="r8_test",
                prefer_local=False,
            )

            order = client._get_backend_order()
            # When not preferring local, returns all backends (order may vary)
            assert "replicate" in order

    @pytest.mark.asyncio
    async def test_generate_success_with_local(self):
        """Test successful generation with local backend."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_backend = MockSuccessBackend(name="local", cost=0.0002)
            mock_local.return_value = mock_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token=None,
            )

            result = await client.generate("A test prompt")

            assert result.success is True
            assert result.prompt_text == "A test prompt"
            assert result.cost == 0.0002
            assert mock_backend.generation_count == 1

    @pytest.mark.asyncio
    async def test_generate_fallback_to_replicate(self):
        """Test fallback from local to Replicate."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local, \
             patch("generation.multi_backend_client.ReplicateBackend") as mock_replicate:

            # Local fails
            mock_local_backend = MockFailBackend(name="local")
            mock_local.return_value = mock_local_backend

            # Replicate succeeds
            mock_replicate_backend = MockSuccessBackend(name="replicate", cost=0.003)
            mock_replicate.return_value = mock_replicate_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token="r8_test",
            )
            client.backends["local"] = mock_local_backend
            client.backends["replicate"] = mock_replicate_backend

            result = await client.generate("A test prompt")

            assert result.success is True
            assert result.cost == 0.003  # Replicate cost
            assert mock_replicate_backend.generation_count == 1

    @pytest.mark.asyncio
    async def test_generate_all_backends_fail(self):
        """Test when all backends fail."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_backend = MockFailBackend(name="local")
            mock_local.return_value = mock_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token=None,
            )
            client.backends["local"] = mock_backend

            result = await client.generate("A test prompt")

            assert result.success is False
            assert "All backends failed" in result.error

    @pytest.mark.asyncio
    async def test_generate_batch(self, mock_image_bytes):
        """Test batch generation."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_backend = MockSuccessBackend(name="local", cost=0.0002)
            mock_local.return_value = mock_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token=None,
            )
            client.backends["local"] = mock_backend

            requests = [
                GenerationRequest(prompt_id=f"id_{i}", prompt_text=f"Prompt {i}")
                for i in range(5)
            ]

            results, stats = await client.generate_batch(requests, show_progress=False)

            assert len(results) == 5
            assert stats.successful == 5
            assert stats.failed == 0
            assert abs(stats.total_cost - 0.001) < 0.0001  # 5 * 0.0002
            assert mock_backend.generation_count == 5

    @pytest.mark.asyncio
    async def test_backend_stats_tracking(self):
        """Test backend statistics tracking."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_backend = MockSuccessBackend(name="local", cost=0.0002)
            mock_local.return_value = mock_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token=None,
            )
            client.backends["local"] = mock_backend

            # Generate 3 images
            for i in range(3):
                await client.generate(f"Prompt {i}")

            stats = client.backend_stats["local"]
            assert stats.total_requests == 3
            assert stats.successful == 3
            assert stats.failed == 0
            assert abs(stats.total_cost - 0.0006) < 0.0001  # 3 * 0.0002

    @pytest.mark.asyncio
    async def test_cost_tracking_integration(self):
        """Test cost tracker integration."""
        with patch("generation.multi_backend_client.LocalGPUBackend") as mock_local:
            mock_backend = MockSuccessBackend(name="local", cost=0.0002)
            mock_local.return_value = mock_backend

            client = MultiBackendClient(
                local_gpu_enabled=True,
                replicate_token=None,
                budget_limit=10.0,
            )
            client.backends["local"] = mock_backend

            await client.generate("Test prompt")

            summary = client.get_cost_summary()
            assert summary["total_cost"] == 0.0002
            assert summary["generation_count"] == 1
            assert summary["budget_limit"] == 10.0


class TestBackendStats:
    """Test BackendStats dataclass."""

    def test_initialization(self):
        """Test backend stats creation."""
        stats = BackendStats(
            name="test-backend",
            total_requests=100,
            successful=95,
            failed=5,
            total_cost=0.285,
            total_time=150.0,
            avg_generation_time=1.5,
        )

        assert stats.name == "test-backend"
        assert stats.total_requests == 100
        assert stats.successful == 95
        assert stats.failed == 5
        assert stats.total_cost == 0.285

    def test_default_values(self):
        """Test default stat values."""
        stats = BackendStats(name="test")

        assert stats.total_requests == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.total_cost == 0.0
