# BACKLOG.md
## AI Playwright Test Generator

Last updated: 2026-03-05

---

## 🔴 Bugs (Fix Before Next Feature)

### B-001 — LLM generates async standalone tests instead of pytest sync
**Symptom:** Generated tests use `async def`, `asyncio.run()`, `async_playwright` instead of pytest fixtures and sync API  
**Root cause:** System prompt in `src/llm_client.py` explicitly instructs async standalone format — contradicts the decided pytest standard  
**Impact:** Generated tests cannot be run with `pytest`, only with `python test_file.py`  
**Fix:** Update system prompt in `src/llm_client.py` to instruct pytest sync format  
**Note:** `src/llm_client.py` is a protected file — confirm before editing  
**Priority:** High — affects every generated test

---

### B-002 — LLM output occasionally has all imports on one line (missing newlines)
**Symptom:** `SyntaxError` on first line of generated file, e.g. `from playwright.sync_api import Pageimport pytestimport os...`  
**Root cause:** LLM response has newlines stripped somewhere in the `_extract_code()` parsing pipeline  
**Impact:** Generated file cannot be imported or run at all  
**Fix:** Add newline normalisation step in `LLMClient._extract_code()` or `TestGenerator`  
**Priority:** High — makes generated files completely unusable when it occurs

---

### B-003 — Generated tests not saved to `generated_tests/` automatically
**Symptom:** After generating via Streamlit UI, the test only exists in the browser session — not on disk  
**Root cause:** `streamlit_app.py` calls `client.generate_test()` directly, bypassing `TestGenerator.generate_and_save()`  
**Impact:** User must manually copy/paste from the UI tab to a file before running  
**Fix:** Call `generator.generate_and_save()` in the Streamlit pipeline, or add explicit file write after generation  
**Priority:** High — poor UX, especially for non-technical users

---

### B-004 — Ambiguous locators when same label exists on multiple forms
**Symptom:** `strict mode violation: get_by_label("Driver Name") resolved to 2 elements`  
**Root cause:** Mock site has both a vehicle form (`#driverName`) and an add driver form (`#driverNameInput`) — both match `get_by_label("Driver Name")`  
**Impact:** Test fails immediately on fill step  
**Fix (immediate):** Use `page.locator("#driverNameInput")` instead of `get_by_label` in affected tests  
**Fix (long term):** Page context scraper (B-005 / Phase 2) will detect and flag ambiguous labels before generation  
**Priority:** Medium — known workaround exists

---

### B-005 — `launch_ui.sh` starts mock server (not appropriate for general use)
**Symptom:** Running `bash launch_ui.sh` starts the mock insurance site alongside the UI  
**Root cause:** Added for dev convenience during session 2  
**Impact:** Anyone using the tool for their own site gets an unwanted mock server starting  
**Fix:** Move mock server startup to `launch_dev.sh`, keep `launch_ui.sh` clean  
**Priority:** Low — no functional impact, just wrong for distribution

---

## 🟡 Improvements

### I-001 — Page Context Scraper (Phase 2 priority feature)
**What:** Before LLM generation, visit the target URL with a headless browser, extract real interactive elements (inputs, buttons, labels, data-testid attributes), inject as structured context into the LLM prompt  
**Why:** LLM currently invents locators that don't exist on the real page. Scraper provides real selectors, eliminating the need for manual locator fixes after generation  
**Spec:** See `FEATURE_SPEC_page_context_scraper.md`  
**New file:** `src/page_context_scraper.py`  
**Priority:** High — single biggest quality improvement possible

---

### I-002 — Auto-save generated tests to disk
**What:** After LLM generates a test, automatically write it to `generated_tests/test_<slug>.py`  
**Why:** Currently user must copy/paste from UI to file manually before running  
**Where:** `streamlit_app.py` pipeline, after `test_code` is confirmed non-empty  
**Priority:** High — see B-003

---

### I-003 — Replace built-in regex parser with proper `user_story_parser.py` module
**What:** Phase 1 implementation — proper parser supporting Jira AC format, Gherkin, bullets, numbered lists, free-form  
**Why:** Currently using a simple inline regex fallback in `streamlit_app.py`. A proper module allows testing, reuse, and Smart mode decision logic  
**New files:** `src/user_story_parser.py`, `src/story_parser_config.py`, `tests/test_user_story_parser.py`  
**Priority:** High — Phase 1 of roadmap

---

### I-004 — Streamlit: show generated file path after saving
**What:** After auto-save (I-002), display the saved file path in the pipeline log and output section  
**Why:** User needs to know exactly which file to run with pytest  
**Priority:** Medium — dependent on I-002

---

### I-005 — Separate `launch_dev.sh` from `launch_ui.sh`
**What:** Create `launch_dev.sh` that starts Streamlit + mock server. Keep `launch_ui.sh` as Streamlit only  
**Why:** `launch_ui.sh` is intended to be the general-purpose launcher. Mock server is only relevant for dev/demo  
**Priority:** Low

---

### I-006 — `.env.example` update for new OLLAMA_TIMEOUT default
**What:** Update `.env.example` to show `OLLAMA_TIMEOUT=300` instead of `60`  
**Why:** 60 seconds is not enough for `qwen3.5:35b`. New users following the README will hit timeout failures  
**Priority:** Medium

---

### I-007 — README: add Streamlit UI quick start section
**What:** Add a "Quick Start — UI Mode" section above the existing CLI quick start  
**Why:** The Streamlit UI is now the primary interface for non-technical users but isn't mentioned in the README  
**Content:**
```bash
# Start the UI (recommended for non-technical users)
bash launch_ui.sh
# Opens at http://localhost:8501
```
**Priority:** Medium

---

### I-008 — Add `streamlit` to pyproject.toml dependencies
**What:** Add `streamlit>=1.32.0` to `[project].dependencies` in `pyproject.toml`  
**Why:** Currently not in dependencies — `uv sync` won't install it on a fresh clone  
**Command:** `uv add streamlit`  
**Priority:** High — blocks anyone trying to use the UI on a fresh install

---

## 🟢 Nice to Have

### N-001 — Dynamic model list refreshes on sidebar interaction
**What:** Add a refresh button next to the model dropdown that re-runs `ollama list`  
**Why:** Currently model list is fetched once on page load. If user pulls a new model mid-session it won't appear  
**Priority:** Low

---

### N-002 — Show estimated wait time when using large model
**What:** When `qwen3.5:35b` is selected, show a note: "This model takes ~2 minutes to generate"  
**Why:** Users unfamiliar with LLM response times may think the app has frozen  
**Priority:** Low

---

### N-003 — Demo GIF in README
**What:** Screen recording of the full workflow: paste story → generate → download  
**Why:** Visual demonstration is the fastest way to show what the tool does in a job interview or portfolio review  
**Priority:** Low

---

## 📋 Session 2 Completed (2026-03-05)

Items completed this session that are NOT bugs or future work:

- ✅ venv rebuilt after project rename (`vs projects` → `AI-Playwright-Test-Generator`)
- ✅ `uv sync` adopted as standard — pip no longer used
- ✅ `pytest.ini` updated with `--browser=chromium`, `--screenshot=only-on-failure`, `testpaths` includes `generated_tests/`
- ✅ `streamlit_app.py` built — dynamic model list, URL validation, pipeline log, 3 report tabs, ZIP download
- ✅ `.env` loading fixed — explicit `dotenv_path` so it works regardless of Streamlit's cwd
- ✅ `OLLAMA_TIMEOUT=300` confirmed working (pipeline log shows actual timeout value)
- ✅ `mock_insurance_site.html` updated — Add Driver button now opens a working form with correct `aria-label` attributes matching test locators
- ✅ `test_happy_path.py` fixed — rewrote with correct pytest-playwright format (removed broken custom browser fixture)
- ✅ `launch_ui.sh` updated — uses `uv run`, auto-starts mock server, checks if already running
- ✅ `FEATURE_SPEC_page_context_scraper.md` created — full spec for Phase 2 scraper feature
