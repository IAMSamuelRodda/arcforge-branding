#!/usr/bin/env python3
"""
Smoke test to verify all core dependencies are importable.
Tests import success for all packages in requirements.txt.
"""

import sys
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def test_import(module_name: str, import_path: str = None) -> Tuple[bool, str]:
    """
    Attempt to import a module and return success status.

    Args:
        module_name: Display name for the module
        import_path: Actual import path (defaults to module_name)

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    import_path = import_path or module_name
    try:
        __import__(import_path)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def main() -> int:
    """Run all import tests and report results."""

    print(f"\n{BOLD}DesignForge Dependency Smoke Test{RESET}")
    print("=" * 50)

    # Define test cases: (display_name, import_path)
    tests = [
        # Core ML/AI Libraries
        ("PyTorch", "torch"),
        ("TorchVision", "torchvision"),
        ("Transformers", "transformers"),
        ("Pillow", "PIL"),
        ("OpenCV", "cv2"),
        ("Scikit-learn", "sklearn"),
        ("NumPy", "numpy"),

        # Image Generation APIs
        ("aiohttp", "aiohttp"),
        ("httpx", "httpx"),
        ("Replicate", "replicate"),
        ("OpenAI", "openai"),

        # Database
        ("SQLAlchemy", "sqlalchemy"),
        ("aiosqlite", "aiosqlite"),

        # Web Interface
        ("Flask", "flask"),
        ("Jinja2", "jinja2"),
        ("Werkzeug", "werkzeug"),

        # CLI Interface
        ("Rich", "rich"),
        ("Click", "click"),
        ("Inquirer", "inquirer"),

        # Configuration & Utilities
        ("PyYAML", "yaml"),
        ("python-dotenv", "dotenv"),
        ("Pydantic", "pydantic"),

        # Testing & Quality
        ("pytest", "pytest"),
        ("pytest-asyncio", "pytest_asyncio"),
        ("pytest-cov", "pytest_cov"),
        ("Ruff", "ruff"),
        ("mypy", "mypy"),

        # Development
        ("IPython", "IPython"),
        ("JupyterLab", "jupyterlab"),

        # Cost Tracking
        ("tiktoken", "tiktoken"),
    ]

    passed = 0
    failed = 0
    errors: List[Tuple[str, str]] = []

    # Run tests
    for display_name, import_path in tests:
        success, error_msg = test_import(display_name, import_path)

        if success:
            print(f"{GREEN}✓{RESET} {display_name:<20} - OK")
            passed += 1
        else:
            print(f"{RED}✗{RESET} {display_name:<20} - FAILED")
            failed += 1
            errors.append((display_name, error_msg))

    # Summary
    print("\n" + "=" * 50)
    print(f"{BOLD}Summary:{RESET}")
    print(f"  {GREEN}Passed:{RESET} {passed}/{len(tests)}")
    print(f"  {RED}Failed:{RESET} {failed}/{len(tests)}")

    # Error details
    if errors:
        print(f"\n{BOLD}Error Details:{RESET}")
        for module, error in errors:
            print(f"  {RED}✗{RESET} {module}: {error}")

    # Version info for key libraries
    if passed > 0:
        print(f"\n{BOLD}Key Library Versions:{RESET}")
        try:
            import torch
            print(f"  PyTorch: {torch.__version__}")
        except:
            pass

        try:
            import transformers
            print(f"  Transformers: {transformers.__version__}")
        except:
            pass

        try:
            import flask
            print(f"  Flask: {flask.__version__}")
        except:
            pass

    print()

    # Return exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
