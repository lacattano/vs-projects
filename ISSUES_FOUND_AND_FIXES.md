# AI-Playwright-Test-Generator - Issues Found and Fixes

## Overview
This document tracks issues identified in the `AI-Playwright-Test-Generator` repository and the fixes applied. Issues are categorized by type and include the root cause analysis, solution implemented, and impact of each fix.

---

## Issues Identified

### 1. **GitHub Actions CI/CD Pipeline** ⚠️
**Problem:** The GitHub Actions workflow badge was not properly configured for the renamed project.

**Root Cause:** The repository reference in the CI/CD badge was outdated.

**Fix:** Updated the CI/CD pipeline badge to reflect the renamed project repository:
```yaml
[![CI/CD Pipeline](https://github.com/lacattano/AI-Playwright-Test-Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/lacattano/AI-Playwright-Test-Generator/actions)
```

**Impact:** The CI/CD status badge now correctly displays for the `AI-Playwright-Test-Generator` project.

---

### 2. **Path Calculation Problem** ⚠️
**Problem:** The application was calculating paths incorrectly, looking for files in the wrong directory.

**Root Cause:** The path calculation used `Path(__file__).parent.parent` which goes up two levels from the script location, assuming it was in a `src/` subdirectory relative to the project root. However, the path traversal was inconsistent and broke when running from different directories.

**Fix:** Changed to use `Path.cwd()` (current working directory) instead:
```python
GENERATED_TESTS_DIR = Path.cwd() / "generated_tests"
MOCK_SITE_DIR = Path.cwd() / "generated_tests"
```

**Impact:** Users can run the script from any directory and it will correctly find the `generated_tests/` folder relative to where they ran the command.

---

### 3. **Pytest Import in Generated Tests** ⚠️
**Problem:** The LLM was generating tests with `import pytest` in the generated code, but the tests were designed to run standalone with Playwright, not with pytest.

**Root Cause:** The original prompt template didn't explicitly tell the LLM to exclude pytest imports. Playwright tests can run either standalone (without pytest) or with pytest - the LLM chose the pytest variant by default.

**Fix:** Updated the prompt to explicitly instruct the LLM:
```
1. ONLY use `from playwright.sync_api import Page, expect` - DO NOT import pytest.
   - The test will run standalone or with Playwright's built-in runner.
```

**Impact:** Generated tests are now standalone Playwright tests that don't require pytest as a dependency.

---

### 4. **LLM Prompt Structure** ⚠️
**Problem:** The original prompt was too verbose and used XML tags that the LLM might not properly respect.

**Fix:** Restructured the prompt to be more direct and explicit:
- Clear numbered requirements
- Explicit "DO NOT" instructions for unwanted behavior
- Example code structure provided
- Emphasis on Playwright-specific APIs

---

### 5. **Markdown Code Fence Parsing** ⚠️
**Problem:** The LLM outputs markdown code fences (```) around the generated code, and the parser wasn't handling them consistently.

**Fix:** Enhanced the cleaning logic to:
- Detect and skip markdown fences (```python, ```, etc.)
- Auto-detect when the code block starts by looking for Python-specific patterns
- Strip remaining fence characters from beginning and end

---

### 6. **CLI Output Formatting** ⚠️
**Problem:** The CLI output was minimal and didn't provide clear visual hierarchy or status indicators.

**Fix:** Improved formatting with:
- Separator lines and headers
- Emoji icons for visual cues (🚀, ✅, ❌, 🧠, etc.)
- Clearer option menus
- Better error messages with context

---

## Files Modified

| File | Changes |
|------|---------|
| `main.py` | Fixed path calculations, updated prompt template, enhanced CLI output |

---

## Testing Recommendations

1. **Test path handling:** Run the script from different directories to ensure it correctly finds `generated_tests/`
   ```bash
   python main.py
   ```

2. **Test LLM generation:** Generate a test and verify it doesn't include pytest imports

3. **Test mock server:** Run the mock server and verify the HTML file loads correctly
   ```bash
   python main.py  # Then select option 3
   ```

4. **Run a test:** Generate a test and run it against the mock site
   ```bash
   cd generated_tests
   pytest test_example.py
   ```

---

## Next Steps for Improvement

1. **Add more test patterns:** Include common Playwright patterns like:
   - `page.wait_for_selector()` for loading states
   - `page.route()` for API mocking examples
   - Network failure handling

2. **Add documentation:** Create a `PROMPT_EXAMPLES.md` file showing how to craft good feature descriptions

3. **Add error handling:** More robust handling of network errors, Ollama connection issues

4. **Add configuration:** Allow users to specify their own Ollama model, timeout settings, etc.

---

## Summary

The main issues identified and fixed were:
1. **GitHub Actions CI/CD** - Updated repository references and badge URLs
2. **Path calculation** - Fixed by using `Path.cwd()` instead of path traversal
3. **Pytest dependency** - Fixed by explicitly telling the LLM not to include it
4. **Prompt clarity** - Improved with more structured instructions
5. **Code fence parsing** - Enhanced the extraction logic
6. **CLI UX** - Improved with better formatting and visual feedback

These changes make the `AI-Playwright-Test-Generator` tool more robust and easier to use.
