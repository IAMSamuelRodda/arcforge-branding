"""Multi-backend image generation client with intelligent fallback.

Supports:
1. Local GPU (primary, free) via ComfyUI
2. Replicate API (fallback, paid) for reliability
"""

import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO

from PIL import Image
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .backends import GenerationBackend, LocalGPUBackend, ReplicateBackend, BackendConfig
from .sd_client import (
    GenerationRequest,
    GenerationResult,
    GenerationStats,
    CostTracker,
)


@dataclass
class BackendStats:
    """Statistics for a backend."""

    name: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_cost: float = 0.0
    total_time: float = 0.0
    avg_generation_time: float = 0.0


class MultiBackendClient:
    """
    Image generation client with multiple backends and intelligent fallback.

    Primary: Local GPU (free, fast)
    Fallback: Replicate API (paid, reliable)
    """

    def __init__(
        self,
        # Local GPU settings
        local_gpu_enabled: bool = True,
        local_gpu_url: str = "http://localhost:8188",
        local_gpu_model: str = "flux-schnell",
        # Replicate settings
        replicate_token: Optional[str] = None,
        replicate_model: str = "flux-schnell",
        # General settings
        budget_limit: float = 60.0,
        max_concurrent: int = 50,
        prefer_local: bool = True,
    ):
        """
        Initialize multi-backend client.

        Args:
            local_gpu_enabled: Enable local GPU backend
            local_gpu_url: ComfyUI API URL (e.g., "http://192.168.1.100:8188")
            local_gpu_model: Model for local GPU
            replicate_token: Replicate API token (or REPLICATE_API_TOKEN env)
            replicate_model: Model for Replicate
            budget_limit: Maximum budget in dollars
            max_concurrent: Maximum concurrent requests
            prefer_local: Try local GPU first
        """
        self.prefer_local = prefer_local
        self.max_concurrent = max_concurrent
        self.cost_tracker = CostTracker(budget_limit=budget_limit)

        # Initialize backends
        self.backends: Dict[str, GenerationBackend] = {}

        # Local GPU backend
        if local_gpu_enabled:
            try:
                self.backends["local"] = LocalGPUBackend(
                    api_url=local_gpu_url,
                    model=local_gpu_model,
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize local GPU backend: {e}")

        # Replicate backend
        if replicate_token:
            try:
                self.backends["replicate"] = ReplicateBackend(
                    api_token=replicate_token,
                    model=replicate_model,
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Replicate backend: {e}")

        if not self.backends:
            raise ValueError("No backends available! Enable local GPU or provide Replicate token")

        # Backend statistics
        self.backend_stats: Dict[str, BackendStats] = {
            name: BackendStats(name=name) for name in self.backends.keys()
        }

    async def generate(
        self,
        prompt: str,
        prompt_id: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **parameters,
    ) -> GenerationResult:
        """
        Generate a single image with intelligent backend selection.

        Args:
            prompt: Text prompt
            prompt_id: Optional prompt ID
            width: Image width
            height: Image height
            **parameters: Additional generation parameters

        Returns:
            GenerationResult
        """
        start_time = datetime.now()
        prompt_id = prompt_id or self._generate_prompt_id(prompt)

        # Determine backend order
        backend_order = self._get_backend_order()

        # Try each backend in order
        last_error = None
        for backend_name in backend_order:
            backend = self.backends[backend_name]
            stats = self.backend_stats[backend_name]

            try:
                # Check availability
                if not await backend.is_available():
                    print(f"   ↓ {backend_name} not available, trying next backend...")
                    continue

                # Generate
                image_bytes, gen_time = await backend.generate(
                    prompt, width, height, **parameters
                )

                # Update statistics
                cost = backend.get_cost()
                self.cost_tracker.add_generation(cost, success=True)
                stats.total_requests += 1
                stats.successful += 1
                stats.total_cost += cost
                stats.total_time += gen_time

                generation_time = (datetime.now() - start_time).total_seconds()

                return GenerationResult(
                    prompt_id=prompt_id,
                    prompt_text=prompt,
                    image_url=None,  # Local doesn't have URL
                    image_bytes=image_bytes,
                    generation_time=generation_time,
                    cost=cost,
                    success=True,
                )

            except Exception as e:
                last_error = e
                stats.total_requests += 1
                stats.failed += 1
                print(f"   ✗ {backend_name} failed: {e}")
                continue

        # All backends failed
        generation_time = (datetime.now() - start_time).total_seconds()
        self.cost_tracker.add_generation(0.0, success=False)

        return GenerationResult(
            prompt_id=prompt_id,
            prompt_text=prompt,
            error=f"All backends failed. Last error: {last_error}",
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
        # Estimate costs (assume primary backend)
        primary_backend = self.backends[self._get_backend_order()[0]]
        estimated_cost_per_image = primary_backend.get_cost()

        # Check budget before starting
        budget_check = self.cost_tracker.check_budget(
            len(requests), estimated_cost_per_image
        )

        if not budget_check["within_budget"]:
            print(f"\n⚠️  Budget Warning:")
            print(f"   Planned cost: ${budget_check['planned_cost']:.2f}")
            print(f"   Remaining budget: ${budget_check['remaining_budget']:.2f}")
            print(
                f"   This batch would exceed your budget by ${budget_check['planned_cost'] - budget_check['remaining_budget']:.2f}"
            )
            print(f"\n   Current utilization: {budget_check['budget_utilization']:.1f}%")

            response = input(f"\n   Continue anyway? [y/N]: ")
            if response.lower() != "y":
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
                # Show which backends are available
                backend_status = await self._get_backend_status()
                backends_str = ", ".join(
                    [f"{name} ({'✓' if avail else '✗'})" for name, avail in backend_status.items()]
                )

                task = progress.add_task(
                    f"[cyan]Generating {len(requests)} images [{backends_str}]...",
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
            print(
                f"\n⚠️  Budget Alert: {self.cost_tracker.get_summary()['budget_utilization_pct']:.1f}% of budget used"
            )
            print(f"   Remaining: ${self.cost_tracker.get_summary()['budget_remaining']:.2f}")

        # Show backend statistics
        await self._print_backend_stats()

        return results, stats

    def _get_backend_order(self) -> List[str]:
        """
        Get backend execution order.

        Returns:
            List of backend names in priority order
        """
        if self.prefer_local and "local" in self.backends:
            # Try local first, then replicate
            order = ["local"]
            if "replicate" in self.backends:
                order.append("replicate")
            return order
        else:
            # Try replicate first (or only backend available)
            return list(self.backends.keys())

    async def _get_backend_status(self) -> Dict[str, bool]:
        """Get availability status for all backends."""
        status = {}
        for name, backend in self.backends.items():
            try:
                status[name] = await backend.is_available()
            except Exception:
                status[name] = False
        return status

    async def _print_backend_stats(self):
        """Print backend usage statistics."""
        print("\n📊 Backend Statistics:")
        for name, stats in self.backend_stats.items():
            if stats.total_requests > 0:
                success_rate = (stats.successful / stats.total_requests) * 100
                avg_time = stats.total_time / stats.successful if stats.successful > 0 else 0

                print(f"\n   {name.upper()}:")
                print(f"   • Requests: {stats.successful}/{stats.total_requests} ({success_rate:.1f}% success)")
                print(f"   • Total cost: ${stats.total_cost:.4f}")
                print(f"   • Avg time: {avg_time:.2f}s")

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
        """Close all backends."""
        for backend in self.backends.values():
            await backend.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
