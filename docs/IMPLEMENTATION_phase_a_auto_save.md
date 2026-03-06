# Phase A — Auto-save & Rename

**Feature:** Save, Review & Run Workflow  
**Status:** Ready for implementation  
**Backlog items:** B-003

---

## Objective

- Automatically save generated tests to disk after successful generation
- Provide UI controls for renaming and downloading the test file
- Track saved file path in session state for subsequent operations

---

## ⚠️ Architecture Decision — Helper Functions Location

**Do NOT put helper functions in `streamlit_app.py` and import them in tests.**  
Importing `streamlit_app` outside a Streamlit context triggers `st.set_page_config()` 
and throws an error. 

**Instead:** Create a new file `src/file_utils.py` for the three helper functions.  
`streamlit_app.py` imports from there. Tests import from there directly with no 
Streamlit dependency.

```
src/file_utils.py          ← helper functions live here
streamlit_app.py           ← imports from src.file_utils
tests/test_file_utils.py   ← imports from src.file_utils (no Streamlit needed)
```

---

## New File: `src/file_utils.py`

### 1. `slugify(text: str) -> str`

Converts text to a filesystem-safe filename segment.

**Examples:**
```python
slugify("Add Driver Flow")           # "add_driver_flow"
slugify("User Story #123 (Login)")   # "user_story_123_login"
slugify("Special!@#Chars")           # "special_chars"
slugify("")                          # "unnamed"
slugify("!!!")                       # "unnamed"
slugify("__Test__")                  # "test"
slugify("Test   String")             # "test_string"
```

**Implementation:**
```python
import re

def slugify(text: str) -> str:
    """Convert text to a filesystem-safe filename segment."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9_]', '_', text)
    text = text.strip('_')
    text = re.sub(r'_+', '_', text)
    if not text:
        text = "unnamed"
    return text
```

---

### 2. `save_generated_test(test_code: str, story_text: str = "", base_url: str = "", output_dir: str = "generated_tests") -> str`

Saves test code to disk with a timestamped filename derived from the **user story text** 
(not the URL — the URL gives non-descriptive names like `localhost_8080`).

**Returns:** Absolute path to saved file

**Parameters:**
- `test_code` — the generated test code string
- `story_text` — the user story or feature description (used for filename slug)
- `base_url` — recorded in the file header comment only
- `output_dir` — output directory, defaults to `"generated_tests"`, overrideable for tests

**Implementation:**
```python
from pathlib import Path
from datetime import datetime

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
```

---

### 3. `rename_test_file(old_path: str, new_name: str) -> str`

Renames a test file on disk with validation and collision handling.

**Returns:** New absolute path

**Parameters:**
- `old_path` — current absolute or relative path to the file
- `new_name` — desired new name, with or without `.py` extension, with or without `test_` prefix

**Behaviour:**
- Strips to slug, enforces `test_` prefix, enforces `.py` extension
- If a file with the new name already exists, appends a timestamp to avoid collision
- Raises `FileNotFoundError` if `old_path` does not exist

**Implementation:**
```python
import os
from datetime import datetime

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
```

---

## Changes to `streamlit_app.py`

### 1. Add import at top
```python
from src.file_utils import save_generated_test, rename_test_file, slugify
```

### 2. Add to `_session_defaults` dict
Add these three keys to the existing `_session_defaults` dict so they are 
always initialised and never throw `KeyError`:

```python
_session_defaults: dict[str, object] = {
    "generated_test": None,
    "report_local": None,
    "report_jira": None,
    "report_html": None,
    "generation_log": [],
    "last_run_time": None,
    "last_story": "",
    "criteria_count": 0,
    "parse_method": "",
    # --- Phase A additions ---
    "saved_test_path": None,     # absolute path to saved file on disk
    "test_filename": None,       # just the filename (no path)
    "last_generated_at": None,   # ISO timestamp of last save
}
```

### 3. Reset saved state before new generation
Add this block immediately before the LLM call, so a new generation 
doesn't show stale save info from the previous run:

```python
# Clear previous save state before starting new generation
st.session_state.saved_test_path = None
st.session_state.test_filename = None
st.session_state.last_generated_at = None
```

### 4. Auto-save after successful generation
Find the block where `test_code` is confirmed non-empty and `_log("Test generated successfully")` 
is called. Immediately after that, add:

```python
# Auto-save to disk
try:
    saved_path = save_generated_test(
        test_code=test_code,
        story_text=user_story,      # the user story text from the input field
        base_url=base_url,
        output_dir="generated_tests",
    )
    st.session_state.saved_test_path = saved_path
    st.session_state.test_filename = os.path.basename(saved_path)
    st.session_state.last_generated_at = datetime.now().isoformat()
    _log(f"Saved: {saved_path}", "ok")
except Exception as e:
    _log(f"Auto-save failed: {e}", "warn")
```

### 5. Add save/rename UI section
Add this section below the generated test code display tabs. 
Place it between the existing code tab and the report tabs:

```python
# ── Save & Rename ──────────────────────────────────────────────────────────
if st.session_state.get("saved_test_path"):
    saved_path = st.session_state.saved_test_path
    filename = st.session_state.test_filename

    st.markdown("---")
    st.markdown("### 💾 Saved Test")
    st.code(saved_path, language=None)

    col1, col2 = st.columns([3, 1])
    with col1:
        new_name = st.text_input(
            "Rename test file",
            value=filename,
            key="rename_input",
            help="Edit the filename and click Rename. test_ prefix is enforced automatically.",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # vertical align with input
        if st.button("Rename", key="rename_btn", type="primary"):
            if Path(saved_path).exists():
                try:
                    new_path = rename_test_file(saved_path, new_name)
                    st.session_state.saved_test_path = new_path
                    st.session_state.test_filename = os.path.basename(new_path)
                    st.success(f"Renamed to: `{os.path.basename(new_path)}`")
                    st.rerun()
                except FileNotFoundError:
                    st.error("File no longer exists on disk. Please regenerate.")
                except Exception as e:
                    st.error(f"Rename failed: {e}")
            else:
                st.error("File not found on disk. Please regenerate.")
```

---

## New Test File: `tests/test_file_utils.py`

```python
"""Unit tests for src/file_utils.py helper functions."""

import os
import tempfile
from pathlib import Path

import pytest

from src.file_utils import rename_test_file, save_generated_test, slugify


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Add Driver Flow") == "add_driver_flow"

    def test_numbers(self) -> None:
        assert slugify("User Story 123") == "user_story_123"

    def test_special_chars(self) -> None:
        assert slugify("User Story #123 (Login)") == "user_story_123_login"
        assert slugify("Special!@#Chars") == "special_chars"

    def test_empty(self) -> None:
        assert slugify("") == "unnamed"
        assert slugify("!!!") == "unnamed"

    def test_leading_trailing_underscores(self) -> None:
        assert slugify("__Test__") == "test"

    def test_collapses_multiple_underscores(self) -> None:
        assert slugify("Test   String") == "test_string"


class TestSaveGeneratedTest:
    def test_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test("def test_x(): pass", output_dir=tmpdir)
            assert Path(saved).exists()

    def test_filename_contains_test_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test("def test_x(): pass", output_dir=tmpdir)
            assert os.path.basename(saved).startswith("test_")

    def test_filename_uses_story_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test(
                "def test_x(): pass",
                story_text="Add Driver Flow",
                output_dir=tmpdir,
            )
            assert "add_driver_flow" in os.path.basename(saved)

    def test_filename_does_not_use_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test(
                "def test_x(): pass",
                base_url="http://localhost:8080",
                output_dir=tmpdir,
            )
            assert "localhost" not in os.path.basename(saved)

    def test_header_contains_base_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test(
                "def test_x(): pass",
                base_url="https://staging.example.com",
                output_dir=tmpdir,
            )
            content = Path(saved).read_text()
            assert "https://staging.example.com" in content

    def test_header_shows_not_specified_when_no_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test("def test_x(): pass", output_dir=tmpdir)
            content = Path(saved).read_text()
            assert "Not specified" in content

    def test_file_extension_is_py(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_generated_test("def test_x(): pass", output_dir=tmpdir)
            assert saved.endswith(".py")

    def test_creates_output_dir_if_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_subdir")
            assert not Path(new_dir).exists()
            save_generated_test("def test_x(): pass", output_dir=new_dir)
            assert Path(new_dir).exists()


class TestRenameTestFile:
    def test_basic_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old = Path(tmpdir) / "test_old.py"
            old.write_text("pass")
            new = rename_test_file(str(old), "test_new_name")
            assert not old.exists()
            assert Path(new).exists()
            assert Path(new).name == "test_new_name.py"

    def test_enforces_test_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old = Path(tmpdir) / "test_old.py"
            old.write_text("pass")
            new = rename_test_file(str(old), "mytest")
            assert Path(new).name == "test_mytest.py"

    def test_strips_py_extension_from_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old = Path(tmpdir) / "test_old.py"
            old.write_text("pass")
            new = rename_test_file(str(old), "test_newname.py")
            assert Path(new).name == "test_newname.py"

    def test_collision_appends_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old = Path(tmpdir) / "test_old.py"
            old.write_text("pass")
            existing = Path(tmpdir) / "test_existing.py"
            existing.write_text("pass")
            new = rename_test_file(str(old), "existing")
            assert "test_existing_" in Path(new).name
            assert Path(new).exists()
            assert existing.exists()  # original untouched

    def test_raises_if_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            rename_test_file("/nonexistent/path/test_x.py", "new_name")

    def test_slugifies_new_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old = Path(tmpdir) / "test_old.py"
            old.write_text("pass")
            new = rename_test_file(str(old), "My Test! File")
            assert Path(new).name == "test_my_test_file.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Error Handling Reference

| Scenario | Response |
|----------|----------|
| `generated_tests/` creation fails | Log warn: `"Auto-save failed: {error}"` — generation still shows in UI |
| File write fails | Log warn: `"Auto-save failed: {error}"` |
| Rename with invalid name | After slugify, always valid — no separate error needed |
| Rename file not found | `st.error("File no longer exists on disk. Please regenerate.")` |
| Rename collision | Auto-append timestamp, no error — user sees new name in success message |

---

## Integration Checklist

- [ ] Create `src/file_utils.py` with `slugify`, `save_generated_test`, `rename_test_file`
- [ ] Add `from src.file_utils import ...` to `streamlit_app.py`
- [ ] Add `saved_test_path`, `test_filename`, `last_generated_at` to `_session_defaults`
- [ ] Add reset block before LLM call
- [ ] Add auto-save block after successful generation
- [ ] Add Save & Rename UI section below code tabs
- [ ] Create `tests/test_file_utils.py`
- [ ] Run `pytest tests/test_file_utils.py -v` — all green before committing

---

## Next Steps

Once Phase A is complete and tests pass:
1. Manually verify: generate a test, confirm file appears in `generated_tests/`
2. Manually verify: rename works, old file gone, new file present
3. Manually verify: regenerating clears previous save state in UI
4. Proceed to Phase B (Test Map & Coverage)
