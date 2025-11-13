"""Backend implementations for image generation.

Supports multiple backends:
- LocalGPUBackend: Local GPU via ComfyUI API (free, fast)
- ReplicateBackend: Replicate API (paid, reliable fallback)
"""

import asyncio
import base64
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, Optional, Tuple

import httpx
from PIL import Image
from replicate import Client


@dataclass
class BackendConfig:
    """Configuration for a backend."""

    name: str
    enabled: bool = True
    cost_per_image: float = 0.0
    timeout: float = 30.0
    max_retries: int = 3


class GenerationBackend(ABC):
    """Abstract base class for image generation backends."""

    def __init__(self, config: BackendConfig):
        """
        Initialize backend.

        Args:
            config: Backend configuration
        """
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=config.timeout)

    @abstractmethod
    async def generate(
        self, prompt: str, width: int = 512, height: int = 512, **params
    ) -> Tuple[bytes, float]:
        """
        Generate an image from a prompt.

        Args:
            prompt: Text prompt
            width: Image width
            height: Image height
            **params: Additional generation parameters

        Returns:
            Tuple of (image_bytes, generation_time)

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if backend is available.

        Returns:
            True if backend can accept requests
        """
        pass

    async def close(self):
        """Close HTTP client and cleanup resources."""
        await self.http_client.aclose()

    def get_cost(self) -> float:
        """Get cost per image for this backend."""
        return self.config.cost_per_image


class LocalGPUBackend(GenerationBackend):
    """Backend for local GPU via ComfyUI API."""

    def __init__(
        self,
        api_url: str = "http://localhost:8188",
        model: str = "flux-schnell",
        config: Optional[BackendConfig] = None,
    ):
        """
        Initialize local GPU backend.

        Args:
            api_url: ComfyUI API URL (e.g., "http://192.168.1.100:8188")
            model: Model to use ("flux-schnell", "flux-dev", "sd35")
            config: Backend configuration (defaults to free local)
        """
        if config is None:
            config = BackendConfig(
                name="local-gpu",
                enabled=True,
                cost_per_image=0.0002,  # Electricity cost estimate
                timeout=60.0,  # Local can be slower on first load
            )

        super().__init__(config)
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.workflow_cache: Dict[str, dict] = {}

    async def generate(
        self, prompt: str, width: int = 1024, height: int = 1024, **params
    ) -> Tuple[bytes, float]:
        """
        Generate image via ComfyUI API.

        Args:
            prompt: Text prompt
            width: Image width
            height: Image height
            **params: Additional parameters (steps, guidance_scale, seed)

        Returns:
            Tuple of (image_bytes, generation_time)
        """
        import time

        start_time = time.time()

        # Build ComfyUI workflow
        workflow = self._build_workflow(prompt, width, height, **params)

        # Queue prompt
        response = await self.http_client.post(
            f"{self.api_url}/prompt", json={"prompt": workflow}
        )
        response.raise_for_status()
        prompt_id = response.json()["prompt_id"]

        # Poll for completion
        image_data = await self._poll_for_result(prompt_id)

        generation_time = time.time() - start_time
        return image_data, generation_time

    async def is_available(self) -> bool:
        """Check if ComfyUI API is reachable."""
        try:
            response = await self.http_client.get(f"{self.api_url}/system_stats")
            return response.status_code == 200
        except Exception:
            return False

    async def _poll_for_result(
        self, prompt_id: str, poll_interval: float = 0.5
    ) -> bytes:
        """
        Poll ComfyUI for generation result.

        Args:
            prompt_id: Prompt ID from queue
            poll_interval: Seconds between polls

        Returns:
            Image bytes
        """
        max_polls = int(self.config.timeout / poll_interval)

        for _ in range(max_polls):
            # Check history
            response = await self.http_client.get(f"{self.api_url}/history/{prompt_id}")

            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})

                    # Find image output
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            images = node_output["images"]
                            if images:
                                # Download image
                                filename = images[0]["filename"]
                                subfolder = images[0].get("subfolder", "")
                                image_type = images[0].get("type", "output")

                                return await self._download_image(
                                    filename, subfolder, image_type
                                )

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Generation timed out after {self.config.timeout}s")

    async def _download_image(
        self, filename: str, subfolder: str, image_type: str
    ) -> bytes:
        """Download generated image from ComfyUI."""
        params = {"filename": filename, "subfolder": subfolder, "type": image_type}

        response = await self.http_client.get(f"{self.api_url}/view", params=params)
        response.raise_for_status()
        return response.content

    def _build_workflow(
        self, prompt: str, width: int, height: int, **params
    ) -> dict:
        """
        Build ComfyUI workflow JSON.

        Args:
            prompt: Text prompt
            width: Image width
            height: Image height
            **params: steps, guidance_scale, seed

        Returns:
            ComfyUI workflow dictionary
        """
        # Simplified Flux workflow
        # In production, load from template files based on model
        if self.model in ["flux-schnell", "flux-dev"]:
            return self._build_flux_workflow(prompt, width, height, **params)
        elif self.model == "sd35":
            return self._build_sd35_workflow(prompt, width, height, **params)
        else:
            raise ValueError(f"Unknown model: {self.model}")

    def _build_flux_workflow(
        self, prompt: str, width: int, height: int, **params
    ) -> dict:
        """Build Flux model workflow."""
        steps = params.get("steps", 4)  # Flux Schnell optimized for 4 steps
        seed = params.get("seed", -1)  # -1 for random

        return {
            "1": {
                "inputs": {"text": prompt},
                "class_type": "CLIPTextEncode",
            },
            "2": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": 1.0,  # Flux doesn't use CFG
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["1", 0],
                    "negative": ["5", 0],
                    "latent_image": ["2", 0],
                },
                "class_type": "KSampler",
            },
            "4": {
                "inputs": {"model_name": "flux-schnell.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "5": {
                "inputs": {"text": ""},
                "class_type": "CLIPTextEncode",
            },
            "6": {
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {"filename_prefix": "flux", "images": ["6", 0]},
                "class_type": "SaveImage",
            },
        }

    def _build_sd35_workflow(
        self, prompt: str, width: int, height: int, **params
    ) -> dict:
        """Build SD 3.5 workflow."""
        steps = params.get("steps", 28)
        guidance_scale = params.get("guidance_scale", 7.0)
        seed = params.get("seed", -1)

        return {
            "1": {
                "inputs": {"text": prompt},
                "class_type": "CLIPTextEncode",
            },
            "2": {
                "inputs": {"text": params.get("negative_prompt", "")},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "4": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": guidance_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["5", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["3", 0],
                },
                "class_type": "KSampler",
            },
            "5": {
                "inputs": {"model_name": "sd3.5_large.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "6": {
                "inputs": {"samples": ["4", 0], "vae": ["5", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {"filename_prefix": "sd35", "images": ["6", 0]},
                "class_type": "SaveImage",
            },
        }


class ReplicateBackend(GenerationBackend):
    """Backend for Replicate API (cloud, paid)."""

    MODELS = {
        "flux-schnell": {
            "name": "black-forest-labs/flux-schnell",
            "cost": 0.003,
        },
        "flux-dev": {
            "name": "black-forest-labs/flux-dev",
            "cost": 0.003,
        },
        "sd35": {
            "name": "stability-ai/stable-diffusion-3.5-large",
            "cost": 0.035,
        },
    }

    def __init__(
        self,
        api_token: Optional[str] = None,
        model: str = "flux-schnell",
        config: Optional[BackendConfig] = None,
    ):
        """
        Initialize Replicate backend.

        Args:
            api_token: Replicate API token (or from REPLICATE_API_TOKEN env)
            model: Model to use
            config: Backend configuration
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Replicate API token required (REPLICATE_API_TOKEN env var or api_token param)"
            )

        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")

        self.model = model
        model_config = self.MODELS[model]

        if config is None:
            config = BackendConfig(
                name=f"replicate-{model}",
                enabled=True,
                cost_per_image=model_config["cost"],
                timeout=30.0,
            )

        super().__init__(config)
        self.client = Client(api_token=self.api_token)
        self.model_name = model_config["name"]

    async def generate(
        self, prompt: str, width: int = 1024, height: int = 1024, **params
    ) -> Tuple[bytes, float]:
        """
        Generate image via Replicate API.

        Args:
            prompt: Text prompt
            width: Image width
            height: Image height
            **params: Additional parameters

        Returns:
            Tuple of (image_bytes, generation_time)
        """
        import time

        start_time = time.time()

        # Run generation (blocking in thread pool)
        output = await asyncio.to_thread(
            self.client.run,
            self.model_name,
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                **params,
            },
        )

        # Download image
        if output and len(output) > 0:
            image_url = output[0] if isinstance(output, list) else output
            image_bytes = await self._download_image(image_url)
            generation_time = time.time() - start_time
            return image_bytes, generation_time
        else:
            raise ValueError("No output from Replicate")

    async def is_available(self) -> bool:
        """Check if Replicate API is available."""
        try:
            # Simple check: API token is set
            return bool(self.api_token)
        except Exception:
            return False

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.content
