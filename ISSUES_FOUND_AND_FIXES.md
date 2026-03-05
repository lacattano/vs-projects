# AI-Playwright-Test-Generator — Issues Found and Fixes

## Overview
This document tracks issues identified and fixes applied. Issues are categorised by session.

---

## Session 1 (2026-03-03)

### 1. GitHub Actions CI/CD Badge ⚠️
**Problem:** Badge not configured for renamed project  
**Fix:** Updated repository reference in badge URL  

### 2. Path Calculation Problem ⚠️
**Problem:** `Path(__file__).parent.parent` broke when running from different directories  
**Fix:** Changed to `Path.cwd()` for consistent path resolution  

### 3. Pytest Import in Generated Tests ⚠️
**Problem:** LLM generated `import pytest` but tests were designed as standalone Playwright scripts  
**Fix:** Updated prompt to explicitly say `DO NOT import pytest`  

### 4. LLM Prompt Structure ⚠️
**Problem:** Prompt too verbose, XML tags not respected by LLM  
**Fix:** Restructured with clear numbered rules and explicit DO NOT instructions  

### 5. Markdown Code Fence Parsing ⚠️
**Problem:** LLM wraps output in ` ```python ` fences, parser wasn't handling consistently  
**Fix:** Enhanced `_extract_code()` to detect and strip fences reliably  

### 6. CLI Output Formatting ⚠️
**Problem:** Minimal output, no visual hierarchy  
**Fix:** Added emoji indicators, separator lines, clearer menus  

### 7. CLI Module Architecture 🆕
**Problem:** No proper CLI — only interactive menu  
**Fix:** Built complete `argparse` CLI with `generate`, `test`, `help` subcommands  

### 8. Output Directory Argument Mismatch 🆕
**Problem:** `--output` flag not mapped to `output_dir` parameter  
**Fix:** Added `dest="output_dir"` to argparse definition  

### 9. Report Format LOCAL Not Implemented 🆕
**Problem:** `ReportFormat.LOCAL` enum defined but `_save_local()` not implemented  
**Fix:** Implemented method generating JSON + XML  

### 10. Missing `parse_json` Method 🆕
**Problem:** `InputParser` had no JSON parsing capability  
**Fix:** Added `parse_json()` method  

### 11. Class Name Inconsistency 🆕
**Problem:** `EvidenceGen` imported as `EvidenceGenerator`  
**Fix:** Renamed class to `EvidenceGenerator`  

### 12. Pre-commit Configuration 🆕
**Problem:** No automated linting before commits  
**Fix:** Created `.pre-commit-config.yaml` with ruff lint + format hooks  

---

## Session 2 (2026-03-05)

### 13. Virtual Environment Broken After Project Rename ⚠️
**Problem:** `.venv` had hardcoded paths to old folder name (`vs projects`). `pip` not found. `(vs-projects)` shown instead of correct env name  
**Root cause:** Project folder renamed from `vs projects` to `AI-Playwright-Test-Generator` — venv paths are absolute and don't survive renames  
**Fix:**
```bash
rm -rf .venv
uv sync
source .venv/Scripts/activate
playwright install chromium
```
**Impact:** venv rebuilt cleanly as `(playwright-test-generator)`  
**Prevention:** Always rebuild venv after renaming project folder. Use `uv sync` not `pip install`

---

### 14. `pip` Not Available — Wrong Package Manager ⚠️
**Problem:** Scripts calling `pip install` fail with `pip: command not found`  
**Root cause:** Project uses `uv` as package manager. `pip` is not on PATH  
**Fix:** Updated `launch_ui.sh` to use `uv sync` and `uv run`. Added rule to always use `uv add <package>` instead of `pip install`  
**Long term rule:** Never call `pip` directly in this project

---

### 15. `streamlit_app.py` — Wrong `LLMClient` Constructor Arguments ⚠️
**Problem:** `LLMClient(model=model_name)` threw `unexpected keyword argument 'model'`  
**Root cause:** `LLMClient.__init__` uses `model_name` not `model`  
**Fix:** Changed to `LLMClient(model_name=model_name)`

---

### 16. `streamlit_app.py` — Wrong `TestGenerator` Usage ⚠️
**Problem:** `TestGenerator(client=client)` — constructor doesn't take a `client` argument. `generator.generate()` method doesn't exist  
**Root cause:** Streamlit app written assuming a different API than what's in the protected files  
**Fix:** Changed to `TestGenerator(model_name=model_name)` and called `client.generate_test(user_request)` directly

---

### 17. `OLLAMA_TIMEOUT` Not Loading from `.env` ⚠️
**Problem:** Pipeline log showed `Timeout: 60s` despite `OLLAMA_TIMEOUT=300` in `.env`. LLM kept timing out  
**Root cause:** `load_dotenv()` called without explicit path — Streamlit's working directory differs from project root, so `.env` was not found  
**Fix:**
```python
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
```

---

### 18. `streamlit_app.py` — `Path` Used Before Import ⚠️
**Problem:** `NameError: name 'Path' is not defined` on startup  
**Root cause:** `load_dotenv(dotenv_path=Path(...))` placed before `from pathlib import Path`  
**Fix:** Added `from pathlib import Path` immediately before `load_dotenv` at top of file

---

### 19. Model Dropdown Hardcoded with Non-Existent Models ⚠️
**Problem:** Sidebar dropdown showed `qwen2.5:7b`, `qwen2.5:14b` etc. — none installed locally  
**Root cause:** Options hardcoded at write time, not reflecting actual installed models  
**Fix:** Dynamic population from `ollama list` on sidebar load, falls back to defaults if Ollama unreachable:
```python
result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
lines = result.stdout.strip().splitlines()[1:]
ollama_models = [l.split()[0] for l in lines if l.strip()]
```

---

### 20. Mock Insurance Site — "Add Driver" Button Not Wired Up ⚠️
**Problem:** "Add Driver" button on main policy page did nothing — no form appeared  
**Root cause:** Button had no event listener and no form existed in the HTML  
**Fix:** Added complete Add Driver form to `mock_insurance_site.html` with:
- `aria-label="Driver Name"` on name input (matches `get_by_label`)
- `aria-label="License Number"` on licence input
- `aria-label="Add Driver"` on add button (matches `get_by_role("button", name=...)`)
- `aria-label="Assigned Drivers"` on driver list (matches `get_by_role("list", name=...)`)
- `aria-label="Save Vehicle"` on save button
- `aria-label="Submitting"` on loading indicator
- JavaScript to add drivers to list, enable Save button, show success message

---

### 21. `test_happy_path.py` — Broken Custom Browser Fixture ⚠️
**Problem:** Test defined custom `browser` fixture AND used `page: Page` parameter — two browser instances conflicting. Also had syntax error (all imports on one line)  
**Root cause:** LLM generated class-style test with custom fixture, conflicting with pytest-playwright's built-in `page` fixture  
**Fix:** Rewrote as clean pytest function using built-in `page: Page` fixture only:
```python
def test_main_flow(page: Page) -> None:
    page.goto("http://localhost:8080")
    page.fill('[data-testid="email"]', "...")
```

---

### 22. Ambiguous Locator — Two "Driver Name" Inputs ⚠️
**Problem:** `strict mode violation: get_by_label("Driver Name") resolved to 2 elements`  
**Root cause:** Vehicle update form has `id="driverName"` (Main Driver Name) AND add driver form has `aria-label="Driver Name"` — both match `get_by_label`  
**Immediate fix:** Use `page.locator("#driverNameInput")` for the add driver form input  
**Long term fix:** Page context scraper (see `FEATURE_SPEC_page_context_scraper.md`) will detect label ambiguity before generation  

---

### 23. Generated Tests Not Saved to Disk ⚠️
**Problem:** After generating via Streamlit, test only exists in browser session — not written to `generated_tests/`  
**Root cause:** `streamlit_app.py` calls `client.generate_test()` directly, not `TestGenerator.generate_and_save()`  
**Status:** Known issue, logged as BACKLOG B-003. Workaround: copy from UI tab and save manually  

---

## Files Modified — Session 2

| File | Changes |
|------|---------|
| `streamlit_app.py` | Built from scratch — Streamlit UI with pipeline, dynamic model list, URL validation, reports, downloads |
| `launch_ui.sh` | Rewritten to use `uv run`, auto-start mock server |
| `pytest.ini` | Added `--browser=chromium`, `--screenshot=only-on-failure`, `generated_tests` to testpaths |
| `generated_tests/mock_insurance_site.html` | Added working Add Driver form with correct aria attributes |
| `generated_tests/test_happy_path.py` | Rewrote with correct pytest-playwright format |
| `.env` | Added `OLLAMA_TIMEOUT=300` |
| `BACKLOG.md` | Created — all known issues and improvements |
| `FEATURE_SPEC_page_context_scraper.md` | Created — full spec for Phase 2 scraper |
| `PROJECT_KNOWLEDGE.md` | Updated — reflects session 2 state |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-01 | Initial release with interactive CLI |
| 1.1.0 | 2026-03-03 | CLI overhaul, report generation, multi-format support |
| 1.2.0 | 2026-03-04 | Pre-commit configuration with ruff |
| 1.3.0 | 2026-03-05 | Streamlit UI, venv rebuild, mock site Add Driver form, pytest.ini updates |
