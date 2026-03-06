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
**Fix (long term):** Page context scraper will detect and flag ambiguous labels before generation  
**Priority:** Medium — known workaround exists

---

### B-005 — `launch_ui.sh` starts mock server (not appropriate for general use)
**Symptom:** Running `bash launch_ui.sh` starts the mock insurance site alongside the UI  
**Root cause:** Added for dev convenience during session 2  
**Impact:** Anyone using the tool for their own site gets an unwanted mock server starting  
**Fix:** Move mock server startup to `launch_dev.sh`, keep `launch_ui.sh` clean  
**Priority:** Low — no functional impact, just wrong for distribution

---

## 🟡 Active Improvements

### AI-001 — Page Context Scraper (Phase 2 priority feature)
**What:** Before LLM generation, visit the target URL with a headless browser, extract real interactive elements (inputs, buttons, labels, data-testid attributes), inject as structured context into the LLM prompt  
**Why:** LLM currently invents locators that don't exist on the real page. Scraper provides real selectors, eliminating the need for manual locator fixes after generation  
**Spec:** See `FEATURE_SPEC_page_context_scraper.md`  
**New file:** `src/page_context_scraper.py`  
**Priority:** High — single biggest quality improvement possible

---

### AI-002 — User Story Parser Module (Phase 1)
**What:** Proper parser supporting Jira AC format, Gherkin, bullets, numbered lists, free-form  
**Why:** Currently using a simple inline regex fallback in `streamlit_app.py`. A proper module allows testing, reuse, and Smart mode decision logic  
**New files:** `src/user_story_parser.py`, `src/story_parser_config.py`, `tests/test_user_story_parser.py`  
**Priority:** High — Phase 1 of roadmap

---

### AI-003 — Update `.env.example` for new OLLAMA_TIMEOUT default
**What:** Update `.env.example` to show `OLLAMA_TIMEOUT=300` instead of `60`  
**Why:** 60 seconds is not enough for `qwen3.5:35b`. New users following the README will hit timeout failures  
**Priority:** Medium

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

**Benefits:**
- Access to more powerful models for complex test generation
- Users can choose between free local models and paid cloud models
- Unified interface for testing different LLM capabilities

**Status:** Deferred — Focus on local-first flow first, add cloud providers after core generator works end-to-end

**Priority:** Medium (nice-to-have, Phase 5+)

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
**Recommendation:** Design with API-first approach to enable future n8n integration  
**Priority:** Low (defer until Phase 4 or beyond)
