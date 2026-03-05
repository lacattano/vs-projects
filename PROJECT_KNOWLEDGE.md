# PROJECT_KNOWLEDGE.md

## Project Overview

**AI Playwright Test Generator** - An AI-powered tool that generates Playwright Python test scripts from user stories and produces Jira-ready evidence bundles.

**Repository:** https://github.com/lacattano/AI-Playwright-Test-Generator

**Current Status:** Active development — Streamlit UI working, LLM pipeline connected, demo-ready

---

## Tech Stack

### Core Technologies
- **Python 3.13+** - Modern Python with full type hint support
- **Playwright** - Browser automation framework
- **pytest** - Professional test framework (pytest-playwright integration)
- **Ollama** - Local LLM serving (qwen3.5:35b model)
- **Streamlit** - Non-technical user UI
- **GitHub Actions** - CI/CD pipeline
- **Codecov** - Test coverage tracking
- **uv** - Package manager (NOT pip — always use `uv add` / `uv sync`)

### Key Dependencies
```
playwright>=1.45.0
pytest>=8.0.0
pytest-playwright>=0.4.0
pytest-html
pytest-json-report
ollama>=0.1.0
openai>=1.12.0
python-dotenv>=1.0.0
requests>=2.31.0
streamlit>=1.32.0
```

---

## Architecture Decisions (FINAL)

### ✅ Test Format: Pytest (DECIDED 2026-03-03)
- **Use:** pytest-playwright with sync API
- **Don't use:** Native async/await standalone tests
- **Reason:** Professional standard (90% of QA jobs require pytest), better reporting, rich ecosystem
- **Impact:** All generated tests use pytest fixtures, expect() assertions, organised test discovery

### ✅ Screenshot Link Strategy: Multi-Format (DECIDED 2026-03-03)
- **Generate automatically:** 3 formats per evidence bundle
  1. `report_local.md` - Relative paths for local viewing/sharing
  2. `report_jira.md` - Jira attachment format (`!filename.png|thumbnail!`)
  3. `report.html` - Base64 embedded for email/archive (fully self-contained)
- **Reason:** Each format serves specific purpose, generating all three is fast, no wrong choice possible

### ✅ LLM Usage: Smart Hybrid Mode (DECIDED 2026-03-03)
- **Default mode:** "Smart" (hybrid regex + LLM)
- **Decision logic:**
  - Try regex parsing first (free, instant)
  - Use LLM only if: >3 criteria found, regex finds nothing, ambiguous keywords present
  - User-configurable: Lightweight (regex only), Smart (default), Always LLM

### ✅ UI: Streamlit (DECIDED 2026-03-05)
- **Use:** Streamlit for non-technical user interface
- **Don't use:** Flask/Django/React — too much overhead for this use case
- **Reason:** Pure Python, single file, deployable in one command, fits existing stack
- **Entry point:** `streamlit_app.py` — launch with `bash launch_ui.sh`

### ✅ Package Manager: uv (DECIDED 2026-03-05)
- **Use:** `uv add <package>`, `uv sync`, `uv run`
- **Never use:** `pip install` directly — uv manages the venv and pyproject.toml together
- **Reason:** Project uses uv.lock, pip is not on PATH in this setup

---

## Environment Setup

### Required Environment Variables
```bash
# .env (NEVER COMMIT)
OLLAMA_MODEL=qwen3.5:35b
OLLAMA_TIMEOUT=300
OLLAMA_BASE_URL=http://localhost:11434
```

### Development Setup
```bash
# 1. Clone repository
git clone https://github.com/lacattano/AI-Playwright-Test-Generator
cd AI-Playwright-Test-Generator

# 2. Create virtual environment and install dependencies
uv sync

# 3. Activate venv (Git Bash / Windows)
source .venv/Scripts/activate

# 4. Install playwright browsers
playwright install chromium

# 5. Configure environment
cp .env.example .env
# Edit .env — set OLLAMA_TIMEOUT=300

# 6. Start Ollama (in separate terminal)
ollama serve   # if not already running as a service

# 7. Launch UI
bash launch_ui.sh
```

### Running Tests
```bash
# Run all tests
pytest -v

# Run generated tests only
pytest generated_tests/ -v

# Run with headed browser (see the browser)
pytest generated_tests/ --headed -v

# Run a standalone generated test
python generated_tests/test_name.py
```

---

## File Structure

### Current Structure
```
AI-Playwright-Test-Generator/
├── .github/workflows/
│   └── ci.yml                          # GitHub Actions CI/CD
├── cli/                                # CLI module
│   ├── config.py
│   ├── evidence_generator.py
│   ├── input_parser.py
│   ├── main.py
│   ├── report_generator.py
│   ├── story_analyzer.py
│   └── test_orchestrator.py
├── generated_tests/                    # Output: tests produced BY the tool
│   ├── mock_insurance_site.html        # Mock test environment
│   └── test_*.py                       # Generated test files
├── screenshots/                        # Screenshot evidence storage
├── src/
│   ├── __init__.py
│   ├── llm_client.py                   # ✅ PROTECTED - Ollama API client
│   └── test_generator.py              # ✅ PROTECTED - Test generation logic
├── tests/                              # Unit tests FOR the tool itself
├── .env                                # Local config (NEVER COMMIT)
├── .env.example                        # Template for .env
├── .streamlit/
│   └── config.toml                     # Streamlit theme config
├── launch_ui.sh                        # Start UI + mock server
├── main.py                             # ✅ PROTECTED - CLI entry point
├── pytest.ini                          # Pytest configuration
├── pyproject.toml                      # Project deps (managed by uv)
├── streamlit_app.py                    # Streamlit UI
├── uv.lock                             # Dependency lock file
├── BACKLOG.md                          # Feature backlog (this session)
├── FEATURE_SPEC_page_context_scraper.md # Phase 2 feature spec
└── PROJECT_KNOWLEDGE.md               # This file
```

---

## Protected Files (DO NOT MODIFY Without Explicit Request)

- `src/llm_client.py` - ✅ Working correctly, handles Ollama API
- `src/test_generator.py` - ✅ Working correctly, generates tests
- `main.py` - ✅ Working CLI interface
- `.github/workflows/ci.yml` - ✅ CI/CD configured and working

**Rule:** Always ask before modifying these files.

---

## Forbidden Actions (NEVER DO)

- ❌ **NEVER commit `.env` files** - Contains sensitive configuration
- ❌ **NEVER commit `__pycache__/` directories** - Python bytecode cache
- ❌ **NEVER use `pip install`** - Use `uv add` instead
- ❌ **NEVER use native async format for tests** - pytest sync format is decided
- ❌ **NEVER remove type hints** - Project standard is full type annotation
- ❌ **NEVER force push to main** without explicit request

---

## Common Issues & Solutions

### Issue: venv not activating / wrong environment
**Symptoms:** `(vs-projects)` shown instead of `(playwright-test-generator)`, pip not found
**Cause:** Old venv from renamed project, or wrong terminal
**Solution:**
```bash
rm -rf .venv
uv sync
source .venv/Scripts/activate   # Git Bash / Windows
```

### Issue: LLM Timeout / Empty Response
**Symptoms:** "LLM returned empty response" in pipeline log
**Cause:** OLLAMA_TIMEOUT too low (default 60s), or .env not loading
**Solution:**
- Set `OLLAMA_TIMEOUT=300` in `.env`
- Confirm `.env` is in project root
- `load_dotenv()` must be called before LLMClient initialises

### Issue: Generated Tests Fail Immediately
**Symptoms:** `SyntaxError` or `NameError: name 'self' is not defined`
**Cause:** LLM output missing newlines (all imports on one line), or class/function style mixed
**Solution:** This is a known generator bug — see BACKLOG.md item B-001

### Issue: Locator Resolves to Multiple Elements
**Symptoms:** `strict mode violation: get_by_label("X") resolved to 2 elements`
**Cause:** Same label exists on multiple forms (e.g. vehicle form + add driver form)
**Solution:** Use specific ID locator: `page.locator("#specificId")` instead of `get_by_label`

### Issue: `bash` command not found
**Symptoms:** Running `bash launch_ui.sh` fails
**Cause:** You're in PowerShell, not Git Bash
**Solution:** Switch terminal to Git Bash, or run `uv run streamlit run streamlit_app.py`

### Issue: Port 8501 already in use
**Symptoms:** `Port 8501 is not available`
**Cause:** Previous Streamlit instance still running
**Solution:** `taskkill //F //IM streamlit.exe` (PowerShell) or `pkill -f streamlit` (Git Bash)

### Issue: Ollama "address already in use"
**Symptoms:** `Error: listen tcp 127.0.0.1:11434: bind: Only one usage`
**Cause:** Ollama is already running — this is fine, ignore the error

---

## Models Available Locally
| Model | Size | Use |
|-------|------|-----|
| `qwen3.5:35b` | 23 GB | Best quality output, ~2 min response |
| `qwen2.5-coder:1.5b-base` | 986 MB | Fast testing, ~6 sec response, simpler output |

---

## Implementation Roadmap

### ✅ Phase 0: Setup & Cleanup (Complete)
- venv issues resolved, uv adopted as package manager
- pytest.ini configured with playwright settings
- CI/CD working

### ✅ Phase UI: Streamlit Interface (Complete — 2026-03-05)
- `streamlit_app.py` built and running
- Dynamic Ollama model list from `ollama list`
- URL validation (button disabled until URL entered)
- Pipeline log with timeout visibility
- All 3 report format tabs + download buttons
- Bundle ZIP download
- `.env` loading fixed with explicit path

### 🚧 Phase 1: Input Format Flexibility (Next)
**Goal:** Replace built-in regex fallback with proper parser module
**Files to Create:**
- `src/user_story_parser.py`
- `src/story_parser_config.py`
- `tests/test_user_story_parser.py`

### 🚧 Phase 2: Page Context Scraper
**Goal:** Visit target URL before generation, inject real DOM selectors into LLM prompt
**Spec:** See `FEATURE_SPEC_page_context_scraper.md`
**Files to Create:**
- `src/page_context_scraper.py`

### 🚧 Phase 3: Evidence Collection
- `src/screenshot_manager.py`
- `reports/jira_reporter.py`
- `reports/evidence_bundle_generator.py`

### 🚧 Phase 4: Test Orchestration
- `src/test_suite_executor.py`
- `src/result_aggregator.py`
- Auto-save generated files to `generated_tests/`

---

## Resources & Links

- **Repository:** https://github.com/lacattano/AI-Playwright-Test-Generator
- **Playwright Docs:** https://playwright.dev/python/
- **pytest Docs:** https://docs.pytest.org/
- **Ollama Docs:** https://ollama.com/docs
- **Streamlit Docs:** https://docs.streamlit.io

---

## Version History

- **2026-03-03:** Initial creation, Phase 1-4 roadmap defined, architecture decisions finalised
- **2026-03-05:** Session 2 — Streamlit UI built and connected, venv issues resolved, uv adopted, mock site updated with Add Driver form, pytest.ini updated, BACKLOG.md created

---

*Last Updated: 2026-03-05*
*Project Status: Active Development*
*Current Phase: UI complete, Phase 1 next*
