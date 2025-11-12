"""
Smoke tests for DesignForge automation module.
These tests verify basic functionality and imports.
"""

import pytest


def test_imports():
    """Test that core dependencies can be imported."""
    # Core ML/AI
    import torch
    import transformers
    import PIL
    import cv2
    import sklearn
    import numpy

    # APIs
    import aiohttp
    import httpx
    import replicate
    import openai

    # Database
    import sqlalchemy
    import aiosqlite

    # Web & CLI
    import flask
    import rich
    import click

    # Utils
    import yaml
    import pydantic

    assert torch.__version__
    assert transformers.__version__


def test_python_version():
    """Test that Python version is 3.11+."""
    import sys

    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"


def test_cuda_available():
    """Test CUDA availability (informational, not required)."""
    import torch

    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not available (CPU mode)")


@pytest.mark.asyncio
async def test_async_support():
    """Test async/await support."""
    import asyncio

    async def dummy_coroutine():
        await asyncio.sleep(0.001)
        return "success"

    result = await dummy_coroutine()
    assert result == "success"
