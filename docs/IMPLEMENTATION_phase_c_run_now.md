# Phase C — Run Now

**Feature:** Save, Review & Run Workflow  
**Status:** Ready for implementation  
**Backlog items:** B-004

---

## Objective

- Add "Run Now" button to execute Playwright tests from the generated test file
- Capture and display test output with colors (green=pass, red=fail)
- Handle errors gracefully with informative messages
- Provide real-time feedback on test execution

---

## Implementation Overview

The "Run Now" button will:
1. Execute `playwright test <saved_test_file>` via subprocess
2. Capture stdout and stderr
3. Display results with colorized output
4. Show summary (passed/failed tests)

---

## Helper Function

### `run_playwright_test(file_path: str) -> tuple[bool, str]`

Executes Playwright test and returns (success, output).

**Implementation:**
```python
import subprocess
from typing import Tuple

def run_playwright_test(file_path: str, output_dir: str = "test_output") -> Tuple[bool, str]:
    """
    Run Playwright tests from a generated test file.
    
    Args:
        file_path: Path to the test file to execute
        output_dir: Directory for Playwright test reports (optional)
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    import os
    from pathlib import Path
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        # Execute playwright test command
        result = subprocess.run(
            ["playwright", "test", file_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout + result.stderr
        
        # Check if tests passed
        success = result.returncode == 0
        
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, "ERROR: Test execution timed out (5 minute limit exceeded)"
    except FileNotFoundError:
        return False, "ERROR: Playwright is not installed or not in PATH. Run: pip install playwright && playwright install"
    except Exception as e:
        return False, f"ERROR: Failed to run tests: {str(e)}"
```

---

## UI Changes in `streamlit_app.py`

### Run Button Component

```python
def display_run_button(saved_file_path: str) -> str:
    """
    Display Run Now button and execute tests.
    
    Args:
        saved_file_path: Path to the saved test file
        
    Returns:
        Test output string
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        run_button = st.button("▶️ Run Now", use_container_width=True, type="primary")
    
    test_output = ""
    
    if run_button:
        with st.spinner("Running tests..."):
            success, output = run_playwright_test(saved_file_path)
            test_output = output
        
        # Display results
        if success:
            st.success("✅ All tests passed!")
        else:
            st.error("❌ Some tests failed")
        
        # Show output in collapsible section
        with st.expander("📄 Test Output", expanded=not success):
            st.code(output, language="plaintext")
    
    return test_output
```

### Combined Workflow Integration

**After Phase A + B, the complete flow:**

```python
# After generating and saving test
if st.button("✨ Generate Test"):
    with st.spinner("Generating test..."):
        # Generate test code
        test_code = generate_test_for_story(prompt_text, base_url, llm_client)
        
        if test_code:
            # Phase A: Save test
            saved_path = save_generated_test(test_code, base_url)
            
            # Show success
            st.success(f"Test saved as: {saved_path}")
            
            # Phase B: Coverage analysis
            try:
                test_functions = parse_test_file(saved_path)
                criteria_list = extract_criteria_from_prompt(prompt_text)
                coverage_list = map_tests_to_criteria(criteria_list, test_functions)
                coverage_stats = calculate_coverage(coverage_list)
                display_coverage(coverage_list, coverage_stats)
            except Exception as e:
                st.warning(f"Could not analyze coverage: {e}")
            
            # Phase C: Run button
            test_output = display_run_button(saved_path)
```

---

## Color Output Handling

Playwright outputs ANSI color codes. To display properly in Streamlit:

```python
def format_test_output_for_streamlit(output: str) -> str:
    """
    Convert ANSI color codes to Streamlit-compatible format.
    
    Streamlit's st.code() supports basic highlighting.
    For full color support, use custom HTML/CSS.
    
    Args:
        output: Raw test output with ANSI codes
        
    Returns:
        Formatted output string
    """
    # Remove ANSI codes for plain code block
    import re
    ansi_pattern = r'\x1b\[[0-9;]*m'
    clean_output = re.sub(ansi_pattern, '', output)
    
    return clean_output
```

Alternatively, use Streamlit's HTML support for colored output:

```python
def display_colored_output(output: str):
    """Display test output with colors preserved."""
    import re
    
    # ANSI color codes to HTML spans
    color_map = {
        r'\x1b\[32m': '<span style="color: green;">',  # Green (pass)
        r'\x1b\[31m': '<span style="color: red;">',    # Red (fail)
        r'\x1b\[33m': '<span style="color: orange;">', # Yellow (warning)
        r'\x1b\[0m': '</span>',                          # Reset
    }
    
    html_output = output
    for ansi, html in color_map.items():
        html_output = re.sub(ansi, html, html_output)
    
    st.markdown(f'<pre style="background: #1e1e1e; padding: 10px; border-radius: 5px;">{html_output}</pre>', unsafe_allow_html=True)
```

---

## Error Handling

| Scenario | Response |
|------|------|
| Test file doesn't exist | Show error: "Test file not found. Please generate a test first." |
| Playwright not installed | Show error: "Playwright not installed. Run: `pip install playwright && playwright install`" |
| Test execution timeout | Show error: "Test execution timed out (5 minute limit)." |
| Test failure | Show error with output, but don't block UI |
| Syntax error in test file | Show warning: "Cannot run test with syntax errors. Check the generated code." |

---

## UI Layout Suggestion

```
┌─────────────────────────────────────────┐
│ ✨ Generate Test                         │
├─────────────────────────────────────────┤
│ 📁 Test saved: tests/example_test.py    │
├─────────────────────────────────────────┤
│ 📊 Test Coverage: 100% (3/3)             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%         │
├─────────────────────────────────────────┤
│ ▶️ Run Now    📋 View Test Code          │
├─────────────────────────────────────────┤
│ ✅ All tests passed!                     │
│                                         │
│ [Test Output Collapsed]                  │
└─────────────────────────────────────────┘
```

---

## Integration Checklist

- [ ] Add `run_playwright_test()` helper to `streamlit_app.py`
- [ ] Add `display_run_button()` UI component to `streamlit_app.py`
- [ ] Add `format_test_output_for_streamlit()` helper (optional)
- [ ] Integrate run button after test generation/saving
- [ ] Add error handling for missing file, playwright not installed
- [ ] Add timeout handling for long test runs
- [ ] Test run button functionality end-to-end

---

## Testing Phase C

### Unit tests (tests/test_phase_c_helpers.py):

```python
import pytest
from unittest.mock import patch, MagicMock
from streamlit_app import run_playwright_test

def test_run_playwright_test_success(mocker):
    """Test successful test execution."""
    # Mock subprocess.run
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "tests passed"
    mock_result.stderr = ""
    
    mocker.patch("subprocess.run", return_value=mock_result)
    
    success, output = run_playwright_test("tests/example.py")
    
    assert success is True
    assert "tests passed" in output

def test_run_playwright_test_failure(mocker):
    """Test failed test execution."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "1 failed"
    
    mocker.patch("subprocess.run", return_value=mock_result)
    
    success, output = run_playwright_test("tests/example.py")
    
    assert success is False
    assert "failed" in output

def test_run_playwright_test_timeout(mocker):
    """Test timeout handling."""
    from subprocess import TimeoutExpired
    
    mocker.patch("subprocess.run", side_effect=TimeoutExpired(cmd="playwright test", timeout=5))
    
    success, output = run_playwright_test("tests/example.py")
    
    assert success is False
    assert "timed out" in output
```

---

## User Flow

1. User enters user story prompt
2. User clicks "✨ Generate Test"
3. Test is generated and saved automatically (Phase A)
4. Coverage analysis displays (Phase B)
5. User sees "▶️ Run Now" button
6. User clicks "▶️ Run Now"
7. Tests execute in background
8. Results display with pass/fail status
9. Full output available in collapsible section

---

## Next Steps

After Phase C:
1. All three phases complete
2. Full workflow tested end-to-end
3. Ready for production use

---

**End of Phase C Implementation Document**