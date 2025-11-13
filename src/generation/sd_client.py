"""Stable Diffusion API client for image generation.

Uses Replicate API with Flux Schnell model for cost-effective generation.
Cost: $0.003 per image (10x cheaper than SD 3.5).
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO

import httpx
from replicate import Client
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from PIL import Image


@dataclass
class GenerationRequest:
    """A single image generation request."""

    prompt_id: str
    prompt_text: str
    parameters: Dict[str, any] = field(default_factory=dict)
    model_format: str = "flux"  # flux, sd35, dalle


@dataclass
class GenerationResult:
    """Result of an image generation."""

    prompt_id: str
    prompt_text: str
    image_url: Optional[str] = None
    image_bytes: Optional[bytes] = None
    error: Optional[str] = None
    generation_time: float = 0.0
    cost: float = 0.003  # Default Flux cost
    success: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GenerationStats:
    """Statistics for a generation session."""

    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_cost: float = 0.0
    total_time: float = 0.0
    avg_generation_time: float = 0.0


class CostTracker:
    """Track generation costs and enforce budget limits."""

    def __init__(self, budget_limit: float = 60.0):
        """
        Initialize cost tracker.

        Args:
            budget_limit: Maximum budget in dollars (default: $60)
        """
        self.budget_limit = budget_limit
        self.session_cost = 0.0
        self.total_cost = 0.0
        self.generation_count = 0
        self.cost_history: List[Dict[str, any]] = []

    def add_generation(self, cost: float, success: bool = True) -> None:
        """Record a generation and its cost."""
        if success:
            self.session_cost += cost
            self.total_cost += cost
            self.generation_count += 1

        self.cost_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "cost": cost,
                "success": success,
                "session_total": self.session_cost,
                "cumulative_total": self.total_cost,
            }
        )

    def check_budget(self, planned_generations: int, cost_per_generation: float = 0.003) -> Dict[str, any]:
        """
        Check if planned generations fit within budget.

        Args:
            planned_generations: Number of images to generate
            cost_per_generation: Cost per image (default: Flux $0.003)

        Returns:
            Dictionary with budget check results
        """
        planned_cost = planned_generations * cost_per_generation
        remaining_budget = self.budget_limit - self.total_cost

        return {
            "within_budget": planned_cost <= remaining_budget,
            "planned_cost": planned_cost,
            "remaining_budget": remaining_budget,
            "budget_utilization": (self.total_cost / self.budget_limit) * 100,
            "budget_limit": self.budget_limit,
            "current_total": self.total_cost,
        }

    def should_alert(self, threshold: float = 0.8) -> bool:
        """Check if budget alert should be triggered."""
        return (self.total_cost / self.budget_limit) >= threshold

    def get_summary(self) -> Dict[str, any]:
        """Get cost tracking summary."""
        return {
            "total_cost": self.total_cost,
            "session_cost": self.session_cost,
            "generation_count": self.generation_count,
            "avg_cost_per_image": self.total_cost / self.generation_count if self.generation_count > 0 else 0,
            "budget_limit": self.budget_limit,
            "budget_remaining": self.budget_limit - self.total_cost,
            "budget_utilization_pct": (self.total_cost / self.budget_limit) * 100,
        }

    def export_history(self, output_path: Path) -> None:
        """Export cost history to JSON file."""
        import json

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": self.get_summary(),
                    "history": self.cost_history,
                },
                f,
                indent=2,
            )


class StableDiffusionClient:
    """Client for Stable Diffusion image generation via Replicate API."""

    # Model configurations
    MODELS = {
        "flux": {
            "name": "black-forest-labs/flux-schnell",
            "cost": 0.003,
            "speed": "fast",  # 1-2 seconds
        },
        "sd35": {
            "name": "stability-ai/stable-diffusion-3.5-large",
            "cost": 0.035,
            "speed": "medium",  # 3-5 seconds
        },
    }

    def __init__(
        self,
        api_token: Optional[str] = None,
        model: str = "flux",
        budget_limit: float = 60.0,
        max_concurrent: int = 50,
    ):
        """
        Initialize SD client.

        Args:
            api_token: Replicate API token (or from REPLICATE_API_TOKEN env var)
            model: Model to use ('flux' or 'sd35')
            budget_limit: Maximum budget in dollars
            max_concurrent: Maximum concurrent requests
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("Replicate API token required (REPLICATE_API_TOKEN env var or api_token param)")

        self.model = model
        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")

        self.model_config = self.MODELS[model]
        self.client = Client(api_token=self.api_token)
        self.cost_tracker = CostTracker(budget_limit=budget_limit)
        self.max_concurrent = max_concurrent

        # HTTP client for downloading images
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def generate(
        self,
        prompt: str,
        prompt_id: Optional[str] = None,
        **parameters,
    ) -> GenerationResult:
        """
        Generate a single image from a prompt.

        Args:
            prompt: Text prompt for generation
            prompt_id: Optional ID to track this prompt
            **parameters: Additional model parameters

        Returns:
            GenerationResult with image data or error
        """
        start_time = datetime.now()
        prompt_id = prompt_id or self._generate_prompt_id(prompt)

        try:
            # Run generation
            output = await asyncio.to_thread(
                self.client.run,
                self.model_config["name"],
                input={"prompt": prompt, **parameters},
            )

            # Download image
            if output and len(output) > 0:
                image_url = output[0] if isinstance(output, list) else output
                image_bytes = await self._download_image(image_url)

                generation_time = (datetime.now() - start_time).total_seconds()

                # Track cost
                self.cost_tracker.add_generation(self.model_config["cost"], success=True)

                return GenerationResult(
                    prompt_id=prompt_id,
                    prompt_text=prompt,
                    image_url=image_url,
                    image_bytes=image_bytes,
                    generation_time=generation_time,
                    cost=self.model_config["cost"],
                    success=True,
                )
            else:
                raise ValueError("No output from model")

        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()
            self.cost_tracker.add_generation(0.0, success=False)

            return GenerationResult(
                prompt_id=prompt_id,
                prompt_text=prompt,
                error=str(e),
                generation_time=generation_time,
                success=False,
            )

    async def generate_batch(
        self,
        requests: List[GenerationRequest],
        show_progress: bool = True,
    ) -> tuple[List[GenerationResult], GenerationStats]:
        """
        Generate multiple images in parallel with progress tracking.

        Args:
            requests: List of generation requests
            show_progress: Show rich progress bar

        Returns:
            Tuple of (results, stats)
        """
        # Check budget before starting
        budget_check = self.cost_tracker.check_budget(
            len(requests), self.model_config["cost"]
        )

        if not budget_check["within_budget"]:
            print(f"\n⚠️  Budget Warning:")
            print(f"   Planned cost: ${budget_check['planned_cost']:.2f}")
            print(f"   Remaining budget: ${budget_check['remaining_budget']:.2f}")
            print(f"   This batch would exceed your budget by ${budget_check['planned_cost'] - budget_check['remaining_budget']:.2f}")
            print(f"\n   Current utilization: {budget_check['budget_utilization']:.1f}%")

            response = input(f"\n   Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                print("   Batch generation cancelled.")
                return [], GenerationStats()

        results = []
        start_time = datetime.now()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def generate_with_semaphore(request: GenerationRequest):
            async with semaphore:
                return await self.generate(
                    request.prompt_text,
                    prompt_id=request.prompt_id,
                    **request.parameters,
                )

        # Run with progress bar
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Generating {len(requests)} images with {self.model}...",
                    total=len(requests),
                )

                # Create tasks
                tasks = [generate_with_semaphore(req) for req in requests]

                # Process as they complete
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    results.append(result)
                    progress.update(task, advance=1)
        else:
            # No progress bar
            tasks = [generate_with_semaphore(req) for req in requests]
            results = await asyncio.gather(*tasks)

        # Calculate stats
        total_time = (datetime.now() - start_time).total_seconds()
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        stats = GenerationStats(
            total_requests=len(requests),
            successful=len(successful),
            failed=len(failed),
            total_cost=sum(r.cost for r in successful),
            total_time=total_time,
            avg_generation_time=total_time / len(requests) if requests else 0,
        )

        # Budget alert
        if self.cost_tracker.should_alert(threshold=0.8):
            print(f"\n⚠️  Budget Alert: {self.cost_tracker.get_summary()['budget_utilization_pct']:.1f}% of budget used")
            print(f"   Remaining: ${self.cost_tracker.get_summary()['budget_remaining']:.2f}")

        return results, stats

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.content

    def _generate_prompt_id(self, prompt: str) -> str:
        """Generate unique ID for prompt."""
        import hashlib

        return hashlib.md5(prompt.encode()).hexdigest()[:16]

    def save_image(self, result: GenerationResult, output_path: Path) -> None:
        """Save generated image to file."""
        if not result.success or not result.image_bytes:
            raise ValueError(f"Cannot save failed generation: {result.error}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save image
        image = Image.open(BytesIO(result.image_bytes))
        image.save(output_path)

    def get_cost_summary(self) -> Dict[str, any]:
        """Get cost tracking summary."""
        return self.cost_tracker.get_summary()

    def export_cost_history(self, output_path: Path) -> None:
        """Export cost history to JSON."""
        self.cost_tracker.export_history(output_path)

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
