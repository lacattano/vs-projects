# BACKLOG.md
## AI Playwright Test Generator

Last updated: 2026-03-06

---

## ✅ Closed Bugs

### B-001 — LLM generates async standalone tests instead of pytest sync
**Status:** ✅ Fixed 2026-03-06
**Fix applied:** Updated system prompt in `src/llm_client.py` to instruct pytest sync format using `playwright.sync_api`. Removed all async/asyncio instructions. Updated CI mock to return pytest sync format.

---

### B-002 — LLM output occasionally has all imports on one line (missing newlines)
**Status:** ✅ Fixed 2026-03-06
**Fix applied:** Added `normalise_code_newlines()` to `src/file_utils.py`. Called in `generate_test_for_story()` in `streamlit_app.py` after LLM response. 8 unit tests added in `tests/test_normalise_code_newlines.py`.

---

### B-003 — Generated tests not saved to `generated_tests/` automatically
**Status:** ✅ Fixed 2026-03-06
**Fix applied:** Phase A implementation — `save_generated_test()` called automatically after every successful generation in `streamlit_app.py`. File saved with timestamped slug filename. Rename UI added.

---

### B-005 — `launch_ui.sh` starts mock server (not appropriate for general use)
**Status:** ✅ Fixed 2026-03-06
**Fix applied:** Mock server startup block removed from `launch_ui.sh`. Moved to new `launch_dev.sh` with added `trap` for clean Ctrl+C shutdown of both processes.

---

## 🔴 Open Bugs

### B-004 — Ambiguous locators when same label exists on multiple forms
**Symptom:** `strict mode violation: get_by_label("Driver Name") resolved to 2 elements`
**Root cause:** Mock site has both a vehicle form (`#driverName`) and an add driver form (`#driverNameInput`) — both match `get_by_label("Driver Name")`
**Impact:** Test fails immediately on fill step
**Fix (immediate):** Use `page.locator("#driverNameInput")` instead of `get_by_label` in affected tests
**Fix (long term):** Page context scraper (AI-001) will detect and flag ambiguous labels before generation
**Priority:** Medium — known workaround exists, long-term fix comes with AI-001

---

## 🟡 Active Improvements

### AI-001 — Page Context Scraper (Next feature — Phase 2)
**What:** Before LLM generation, visit the target URL with a headless browser, extract real interactive elements (inputs, buttons, labels, data-testid attributes), inject as structured context into the LLM prompt
**Why:** LLM currently invents locators that don't exist on the real page. Scraper provides real selectors, eliminating the need for manual locator fixes after generation
**Spec:** See `FEATURE_SPEC_page_context_scraper.md`
**New file:** `src/page_context_scraper.py`
**Priority:** High — single biggest quality improvement possible

---

### AI-002 — User Story Parser Module
**What:** Proper parser supporting Jira AC format, Gherkin, bullets, numbered lists, free-form
**Why:** Criteria extraction currently lives in `streamlit_app.py` as part of Phase B coverage analysis. A dedicated module allows proper unit testing and reuse by the scraper and other components
**New files:** `src/user_story_parser.py`, `tests/test_user_story_parser.py`
**Priority:** High — Phase 1 of roadmap, also needed cleanly by AI-001

---

### AI-003 — Update `.env.example` for new OLLAMA_TIMEOUT default
**What:** Update `.env.example` to show `OLLAMA_TIMEOUT=300` instead of `60`
**Why:** 60 seconds is not enough for `qwen3.5:35b`. New users following the README will hit timeout failures
**Priority:** Medium — small change, do alongside next feature

---

### AI-004 — Phase C: Run Now gaps
**What:** Several items from the Phase C spec were not implemented in the first pass
**Missing:**
- Environment URL dropdown before Run Now (currently runs against the URL used at generation time)
- Re-run failed tests only button
- Screenshot viewer for captured screenshots
**Priority:** Medium — core Run Now works, these are UX improvements

---

### AI-005 — Coverage helpers should move to `src/coverage_utils.py`
**What:** `parse_test_functions()`, `extract_criteria_from_user_story()`, `map_tests_to_criteria()`, `calculate_coverage()` and the two dataclasses are currently defined in `streamlit_app.py`
**Why:** Any unit tests that import them will trigger `st.set_page_config()` and crash — same problem we solved for Phase A with `src/file_utils.py`
**New file:** `src/coverage_utils.py`, `tests/test_coverage_utils.py`
**Priority:** Medium — not blocking anything today, but needed before writing coverage unit tests

---

## 🌟 Nice to Have — Future Enhancements

### Cloud LLM Providers

**Goal:** Support multiple LLM backends beyond local Ollama

**Use Cases:**
1. **OpenRouter** - Unified API access to 50+ models (GPT-4, Claude, Llama, etc.)
2. **OpenAI** - Direct GPT-4 access for complex test scenarios
3. **Anthropic** - Claude models for better instruction following

**Spec:**
- Add `LLM_PROVIDER` environment variable (ollama, openrouter, openai, anthropic)
- Provider-specific API key configuration
- Streamlit UI dropdown for provider selection
- Fallback to Ollama when no API keys configured

**Status:** Deferred — focus on local-first flow first
**Priority:** Medium (Phase 5+)

---

## 🔮 Future Exploration — n8n Integration

### Potential Use Cases

**n8n** is a workflow automation tool that could integrate with the test generator for:

1. **Jira Webhook Automation**
   - Trigger test generation when a story is created/updated in Jira
   - Auto-attach evidence back to Jira tickets

2. **Scheduled Test Execution**
   - Cron-based triggers to run existing test suites
   - Report to Slack/Email/Discord

3. **Multi-System Integration**
   - Sync evidence bundles across cloud storage
   - Create follow-up tickets for flaky tests
   - Parallel execution orchestration

### Implementation Approach

Requires designing an **HTTP API layer**:
```
src/
├── api_server.py              # FastAPI/Flask server
└── api/
    ├── routes/
    │   ├── test_generation.py   # POST /api/generate-test
    │   ├── test_execution.py    # POST /api/execute-tests
    │   └── evidence.py          # POST /api/upload-evidence
    └── auth.py                  # Optional API key validation
```

**Status:** Low priority — Phase 4+ consideration once core functionality is complete
**Priority:** Low (defer until Phase 4 or beyond)
