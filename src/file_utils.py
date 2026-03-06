"""Helper functions for file operations in the Playwright test generator."""

import os
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe filename segment.

    Examples:
        >>> slugify("Add Driver Flow")
        'add_driver_flow'
        >>> slugify("User Story #123 (Login)")
        'user_story_123_login'
        >>> slugify("Special!@#Chars")
        'special_chars'
        >>> slugify("")
        'unnamed'
        >>> slugify("!!!")
        'unnamed'
        >>> slugify("__Test__")
        'test'
        >>> slugify("Test   String")
        'test_string'
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9_]", "_", text)
    text = text.strip("_")
    text = re.sub(r"_+", "_", text)
    if not text:
        text = "unnamed"
    return text


def save_generated_test(
    test_code: str,
    story_text: str = "",
    base_url: str = "",
    output_dir: str = "generated_tests",
) -> str:
    """
    Save test code to <output_dir>/test_YYYYMMDD_HHMMSS_<slug>.py

    Args:
        test_code:  The generated test code as a string
        story_text: User story text — used for the filename slug
        base_url:   Recorded in file header comment only
        output_dir: Output directory (default: generated_tests)

    Returns:
        Absolute path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    story_slug = slugify(story_text[:50]) if story_text else "test"
    filename = f"test_{timestamp}_{story_slug}.py"
    file_path = output_path / filename

    header = f'''"""
Auto-generated Playwright test
Generated: {datetime.now().isoformat()}
Base URL:  {base_url or "Not specified"}
"""

'''
    file_path.write_text(header + test_code, encoding="utf-8")
    return str(file_path.absolute())


def rename_test_file(old_path: str, new_name: str) -> str:
    """
    Rename a test file on disk.

    Args:
        old_path: Current file path
        new_name: Desired new name (extension and test_ prefix optional)

    Returns:
        New absolute path

    Raises:
        FileNotFoundError: If old_path doesn't exist
    """
    old_path_obj = Path(old_path)
    if not old_path_obj.exists():
        raise FileNotFoundError(f"File not found: {old_path}")

    # Sanitise
    new_name = new_name.removesuffix(".py")
    new_name = slugify(new_name)

    # Enforce test_ prefix
    if not new_name.startswith("test_"):
        new_name = f"test_{new_name}"

    new_path = old_path_obj.parent / f"{new_name}.py"

    # Handle collision — append timestamp
    if new_path.exists() and new_path != old_path_obj:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = old_path_obj.parent / f"{new_name}_{ts}.py"

    os.rename(old_path, new_path)
    return str(new_path.absolute())
