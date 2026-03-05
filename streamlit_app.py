"""
streamlit_app.py — AI Playwright Test Generator UI
A clean, terminal-inspired interface for non-technical QA testers.
"""

import io
import os
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")  # explicit path so it works regardless of cwd

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="AI Test Generator",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* ── Dark background ── */
.stApp {
    background-color: #0d0f14;
    color: #e2e8f0;
}

/* ── Hide default header ── */
header[data-testid="stHeader"] { background: transparent; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #111318;
    border-right: 1px solid #1e2330;
}
[data-testid="stSidebar"] * { color: #c8d0e0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #7a8aaa !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Logo / Hero ── */
.hero-block {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #1e2330;
    margin-bottom: 2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: #f0f4ff;
    letter-spacing: -0.02em;
    line-height: 1;
    margin: 0;
}
.hero-title span { color: #4ade80; }
.hero-sub {
    font-size: 0.85rem;
    color: #556070;
    margin-top: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #4ade80;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.4rem;
    display: block;
}

/* ── Input boxes ── */
.stTextArea textarea, .stTextInput input {
    background-color: #13161f !important;
    border: 1px solid #1e2533 !important;
    border-radius: 6px !important;
    color: #dde4f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    caret-color: #4ade80;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.12) !important;
}
.stTextArea label, .stTextInput label {
    color: #7a8aaa !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #13161f !important;
    border: 1px solid #1e2533 !important;
    color: #dde4f0 !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"],
.stButton > button {
    background: #4ade80 !important;
    color: #0a0c10 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.02em;
    transition: all 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: #86efac !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(74,222,128,0.25) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #2a3245 !important;
    color: #7ab8f5 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    width: 100%;
    transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover {
    border-color: #7ab8f5 !important;
    background: rgba(122,184,245,0.08) !important;
}

/* ── Code blocks ── */
.stCodeBlock {
    border: 1px solid #1e2533;
    border-radius: 8px;
    overflow: hidden;
}
pre code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111318;
    border-radius: 8px 8px 0 0;
    gap: 0;
    padding: 0.25rem;
    border: 1px solid #1e2330;
    border-bottom: none;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #556070 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    border-radius: 6px !important;
    padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: #1e2533 !important;
    color: #4ade80 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #111318;
    border: 1px solid #1e2330;
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 1rem;
}

/* ── Status / info boxes ── */
.status-box {
    background: #111318;
    border: 1px solid #1e2533;
    border-left: 3px solid #4ade80;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #8ba0b8;
    margin: 0.5rem 0;
}
.status-box.error {
    border-left-color: #f87171;
    color: #f9a8a8;
    background: #150e0e;
}
.status-box.warn {
    border-left-color: #fbbf24;
    color: #fde08a;
    background: #141009;
}

/* ── Log stream ── */
.log-stream {
    background: #090b0f;
    border: 1px solid #1a1f2e;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    line-height: 1.8;
    color: #5a7a5a;
    max-height: 240px;
    overflow-y: auto;
}
.log-stream .ok   { color: #4ade80; }
.log-stream .info { color: #7ab8f5; }
.log-stream .warn { color: #fbbf24; }
.log-stream .err  { color: #f87171; }

/* ── Metric cards ── */
.metric-row {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
}
.metric-card {
    flex: 1;
    background: #111318;
    border: 1px solid #1e2330;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
}
.metric-card .val {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: #4ade80;
    line-height: 1;
}
.metric-card .lbl {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #3d4f5e;
    margin-top: 0.2rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Dividers ── */
hr { border-color: #1e2330 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #111318 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 6px !important;
    color: #7a8aaa !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2533; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #2a3448; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state defaults ───────────────────────────────────────────────────
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
}
for key, val in _session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Helper: try to import project modules ────────────────────────────────────
def _try_import() -> tuple[bool, str]:
    """Attempt to import the src modules; return (success, message)."""
    src_path = Path(__file__).parent / "src"
    if src_path.exists() and str(src_path.parent) not in sys.path:
        sys.path.insert(0, str(src_path.parent))
    try:
        from src.llm_client import LLMClient  # noqa: F401
        from src.test_generator import TestGenerator  # noqa: F401

        return True, "src modules loaded"
    except ImportError as e:
        return False, str(e)


_modules_ok, _modules_msg = _try_import()


def _log(msg: str, level: str = "info") -> None:
    """Append a timestamped message to the session log."""
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.generation_log.append((ts, level, msg))


def _render_log() -> str:
    """Render the log list as HTML for the log-stream div."""
    lines = []
    for ts, level, msg in st.session_state.generation_log[-40:]:
        lines.append(f'<span class="{level}">[{ts}]</span> {msg}')
    return "<br>".join(lines) if lines else '<span class="info">Waiting for input…</span>'


# ── Core generation logic ────────────────────────────────────────────────────
def run_generation(
    story: str,
    base_url: str,
    parse_mode: str,
    model_name: str,
) -> bool:
    """
    Orchestrate test generation. Calls src modules when available,
    falls back to a simulation so the UI is always demonstrable.
    Returns True on success.
    """
    st.session_state.generation_log = []
    st.session_state.generated_test = None
    st.session_state.report_local = None
    st.session_state.report_jira = None
    st.session_state.report_html = None

    _log("Starting pipeline…", "info")

    # ── Step 1: Parse user story ──────────────────────────────────────────
    _log(f"Parse mode: {parse_mode}", "info")
    time.sleep(0.3)

    criteria: list[str] = []

    if _modules_ok:
        try:
            # Try the real parser if it exists
            from src.user_story_parser import UserStoryParser  # type: ignore

            parser = UserStoryParser(mode=parse_mode.lower())
            criteria = parser.parse(story)
            st.session_state.parse_method = "regex" if len(criteria) < 4 else "llm-enhanced"
            _log(f"Parsed {len(criteria)} acceptance criteria via {st.session_state.parse_method}", "ok")
        except ImportError:
            # user_story_parser not built yet — do lightweight regex inline
            criteria = _builtin_parse(story)
            st.session_state.parse_method = "built-in regex"
            _log(f"Parsed {len(criteria)} criteria (built-in regex fallback)", "warn")
    else:
        criteria = _builtin_parse(story)
        st.session_state.parse_method = "built-in regex"
        _log("src modules not found — using built-in parser", "warn")
        _log(f"Parsed {len(criteria)} acceptance criteria", "ok")

    if not criteria:
        _log("No criteria detected — check user story format", "err")
        return False

    st.session_state.criteria_count = len(criteria)

    # ── Step 2: Generate test code ────────────────────────────────────────
    _log(f"Connecting to LLM ({model_name})…", "info")
    time.sleep(0.4)

    test_code: str | None = None

    if _modules_ok:
        try:
            from src.llm_client import LLMClient  # type: ignore

            _log("LLM client initialised", "ok")
            client = LLMClient(model_name=model_name)
            timeout_val = int(os.getenv("OLLAMA_TIMEOUT", "60"))
            _log(f"Timeout: {timeout_val}s · Generating pytest test…", "info")
            user_request = "\n".join(criteria)
            if base_url:
                user_request += f"\n\nBase URL: {base_url}"
            test_code = client.generate_test(user_request)
            if test_code and test_code.strip():
                _log("Test generated successfully", "ok")
            else:
                _log("LLM returned empty response — is Ollama running?", "err")
                _log("Falling back to template generator…", "warn")
                test_code = _builtin_generate(criteria, base_url, model_name)
        except Exception as exc:
            _log(f"LLM error: {exc}", "err")
            _log("Falling back to template generator…", "warn")
            test_code = _builtin_generate(criteria, base_url, model_name)
    else:
        _log("Using template generator (src not loaded)", "warn")
        test_code = _builtin_generate(criteria, base_url, model_name)

    if not test_code:
        _log("Test generation failed", "err")
        return False

    st.session_state.generated_test = test_code
    _log(f"Generated {test_code.count(chr(10))} lines of pytest code", "ok")

    # ── Step 3: Build evidence reports ────────────────────────────────────
    _log("Building evidence bundle…", "info")
    time.sleep(0.2)

    bundle_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.session_state.report_local = _build_local_md(criteria, test_code, bundle_time, base_url)
    _log("report_local.md  ✓", "ok")

    st.session_state.report_jira = _build_jira_md(criteria, test_code, bundle_time, base_url)
    _log("report_jira.md   ✓", "ok")

    st.session_state.report_html = _build_standalone_html(criteria, test_code, bundle_time, base_url)
    _log("report.html      ✓ (self-contained)", "ok")

    st.session_state.last_run_time = bundle_time
    st.session_state.last_story = story[:80] + ("…" if len(story) > 80 else "")
    _log("Pipeline complete 🎉", "ok")
    return True


# ── Built-in lightweight parser (no src dependency) ─────────────────────────
def _builtin_parse(story: str) -> list[str]:
    """Quick regex parser for common user story formats."""
    import re

    criteria: list[str] = []
    lines = story.splitlines()

    bullet_re = re.compile(r"^\s*[-•*]\s+(.+)")
    numbered_re = re.compile(r"^\s*\d+[.)]\s+(.+)")
    should_re = re.compile(r".*(should|must|shall|can|verify|confirm|ensure)\s+(.+)", re.I)
    gherkin_re = re.compile(r"^\s*(given|when|then|and)\s+(.+)", re.I)
    ac_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"acceptance criteria", line, re.I):
            ac_section = True
            continue
        for pattern in [bullet_re, numbered_re, gherkin_re]:
            m = pattern.match(line)
            if m:
                if m.lastindex is not None:
                    criteria.append(m.group(m.lastindex).strip())
                break
        else:
            if ac_section or should_re.match(line):
                m2 = should_re.match(line)
                if m2:
                    criteria.append(line.strip())

    return criteria or [story.strip()[:120]]


# ── Built-in template test generator ────────────────────────────────────────
def _builtin_generate(
    criteria: list[str],
    base_url: str,
    model: str,
) -> str:
    """
    Produce a valid pytest-playwright scaffold when the LLM is unavailable.
    Each criterion becomes a placeholder test.
    """
    url = base_url.rstrip("/") or "https://example.com"
    ts = datetime.now().strftime("%Y-%m-%d")

    lines = [
        '"""',
        "Auto-generated pytest-playwright tests",
        f"Generated : {ts}",
        f"Base URL  : {url}",
        f"Model     : {model} (template fallback — connect Ollama for AI generation)",
        '"""',
        "",
        "import pytest",
        "from playwright.sync_api import Page, expect",
        "",
        "",
        "@pytest.fixture(scope='session')",
        "def base_url() -> str:",
        f'    return "{url}"',
        "",
        "",
    ]

    for i, criterion in enumerate(criteria, 1):
        safe = criterion.lower()
        safe = "".join(c if c.isalnum() or c == "_" else "_" for c in safe)
        safe = safe[:60].strip("_")
        fn = f"test_{safe}" if safe else f"test_criterion_{i}"

        lines += [
            f"def {fn}(page: Page, base_url: str) -> None:",
            '    """',
            f"    Criterion {i}: {criterion}",
            '    """',
            "    page.goto(base_url)",
            f"    # TODO: implement — {criterion[:80]}",
            f"    page.screenshot(path=f'screenshots/{fn}.png')",
            "    # expect(page.locator('...')).to_be_visible()",
            "",
            "",
        ]

    return "\n".join(lines)


# ── Report builders ──────────────────────────────────────────────────────────
def _build_local_md(criteria: list[str], test_code: str, ts: str, url: str) -> str:
    rows = "\n".join(f"| TC-{i:03} | {c[:80]} | ⬜ Pending |" for i, c in enumerate(criteria, 1))
    return f"""# Test Evidence Report — Local
**Generated:** {ts}
**Base URL:** {url}
**Criteria:** {len(criteria)}

## Test Cases
| ID | Criterion | Status |
|----|-----------|--------|
{rows}

## Screenshots
{chr(10).join(f"![TC-{i:03}](screenshots/test_{i:03}.png)" for i in range(1, len(criteria) + 1))}

## Generated Test
```python
{test_code}
```
"""


def _build_jira_md(criteria: list[str], test_code: str, ts: str, url: str) -> str:
    rows = "\n".join(f"|| TC-{i:03} || {c[:80]} || Pending ||" for i, c in enumerate(criteria, 1))
    screenshots = "\n".join(f"!test_{i:03}.png|thumbnail!" for i in range(1, len(criteria) + 1))
    return f"""h2. Test Evidence Report — Jira
*Generated:* {ts}
*Base URL:* {url}

h3. Test Cases
|| ID || Criterion || Status ||
{rows}

h3. Screenshots
{screenshots}

h3. Generated Test
{{code:python}}
{test_code}
{{code}}
"""


def _build_standalone_html(criteria: list[str], test_code: str, ts: str, url: str) -> str:
    import html as _html

    rows_html = "".join(
        f"<tr><td>TC-{i:03}</td><td>{_html.escape(c[:100])}</td>"
        f"<td><span class='badge pending'>Pending</span></td></tr>"
        for i, c in enumerate(criteria, 1)
    )
    code_escaped = _html.escape(test_code)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test Evidence — {ts}</title>
<style>
  body{{font-family:system-ui,sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:2rem}}
  h1{{color:#4ade80;font-size:1.4rem;margin-bottom:0.25rem}}
  .meta{{color:#556070;font-size:0.8rem;margin-bottom:2rem}}
  table{{width:100%;border-collapse:collapse;margin-bottom:2rem}}
  th{{background:#161b22;color:#8b949e;padding:0.5rem 0.75rem;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:.06em}}
  td{{padding:0.5rem 0.75rem;border-bottom:1px solid #21262d;font-size:0.85rem}}
  .badge{{padding:0.15rem 0.6rem;border-radius:20px;font-size:0.7rem;font-weight:600}}
  .pending{{background:#21262d;color:#8b949e}}
  pre{{background:#090c10;border:1px solid #21262d;border-radius:8px;padding:1.2rem;overflow-x:auto;font-size:0.78rem;line-height:1.6}}
  h2{{color:#7ab8f5;font-size:1rem;margin:2rem 0 0.75rem}}
</style>
</head>
<body>
<h1>🎭 Test Evidence Report</h1>
<p class="meta">Generated: {ts} &nbsp;|&nbsp; Base URL: {url} &nbsp;|&nbsp; Criteria: {len(criteria)}</p>
<h2>Test Cases</h2>
<table>
<tr><th>ID</th><th>Criterion</th><th>Status</th></tr>
{rows_html}
</table>
<h2>Generated Test Code</h2>
<pre><code>{code_escaped}</code></pre>
</body>
</html>"""


# ── Build ZIP bundle ─────────────────────────────────────────────────────────
def _build_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if st.session_state.generated_test:
            zf.writestr("generated_test.py", st.session_state.generated_test)
        if st.session_state.report_local:
            zf.writestr("report_local.md", st.session_state.report_local)
        if st.session_state.report_jira:
            zf.writestr("report_jira.md", st.session_state.report_jira)
        if st.session_state.report_html:
            zf.writestr("report.html", st.session_state.report_html)
        zf.writestr(
            "README.txt",
            (
                "Evidence Bundle — AI Playwright Test Generator\n"
                "==============================================\n"
                "  generated_test.py  — run with: pytest generated_test.py\n"
                "  report_local.md    — view locally in any Markdown viewer\n"
                "  report_jira.md     — paste into Jira ticket description\n"
                "  report.html        — open in browser / attach to email\n"
            ),
        )
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# UI LAYOUT
# ═══════════════════════════════════════════════════════════════════════════

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
    <div style="padding:1.2rem 0 1rem 0; border-bottom:1px solid #1e2330; margin-bottom:1.5rem">
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;color:#f0f4ff">
            🎭 AI Test Gen
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#3d5060;margin-top:0.2rem">
            v0.1 · non-tech mode
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<span class="section-label">⚙ Configuration</span>', unsafe_allow_html=True)

    base_url = st.text_input(
        "Application URL",
        placeholder="https://your-app.com",
        help="The URL of the web application you want to test.",
    )

    parse_mode = st.selectbox(
        "Parsing Mode",
        options=["Smart (Recommended)", "Lightweight (Regex Only)", "Always Use LLM"],
        index=0,
        help="Smart uses regex first, then LLM only if needed. Best for most stories.",
    )

    # ── Dynamic model list from ollama ──
    _default_models = ["qwen3.5:35b", "qwen2.5-coder:1.5b-base", "qwen2.5:7b", "llama3.2", "mistral"]
    try:
        import subprocess

        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
        lines = result.stdout.strip().splitlines()[1:]  # skip header
        ollama_models = [line.split()[0] for line in lines if line.strip()]
        available_models = ollama_models if ollama_models else _default_models
    except Exception:
        available_models = _default_models

    model_name = st.selectbox(
        "LLM Model",
        options=available_models,
        index=0,
        help="Models detected from your local Ollama installation.",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">📊 Status</span>', unsafe_allow_html=True)

    if _modules_ok:
        st.markdown(
            '<div class="status-box">✅ src modules loaded</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="status-box warn">⚠ src not found<br><small>{_modules_msg[:60]}</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">📖 Story Formats</span>', unsafe_allow_html=True)
    with st.expander("Supported inputs"):
        st.markdown("""
**Acceptance Criteria:**
```
Acceptance Criteria:
- User can log in with email
- Shows error on wrong password
```

**Gherkin (BDD):**
```
Given I am on the login page
When I enter valid credentials
Then I should see the dashboard
```

**Plain bullets / numbered list:**
```
• Search returns results
• Filter by category works
1. Cart updates on add
```

**Free-form:**
```
The login form should validate
email format and show inline errors.
```
""")


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-block">
    <p class="hero-title">AI <span>Playwright</span> Test Generator</p>
    <p class="hero-sub">paste a user story → get a pytest test + jira evidence bundle</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Input area ───────────────────────────────────────────────────────────────
st.markdown('<span class="section-label">📝 User Story / Acceptance Criteria</span>', unsafe_allow_html=True)

example_stories = {
    "— pick an example —": "",
    "Login form validation": (
        "Acceptance Criteria:\n"
        "- User can log in with a valid email and password\n"
        "- An error message is shown when the password is incorrect\n"
        "- The email field validates format before submission\n"
        "- After 5 failed attempts the account is locked"
    ),
    "Search & filter": (
        "Given I am on the product listing page\n"
        "When I search for 'laptop'\n"
        "Then relevant products should appear\n"
        "And I can filter results by price range\n"
        "And results update without a page reload"
    ),
    "Shopping cart": (
        "• Adding an item increases the cart count badge\n"
        "• Removing an item decreases the total price\n"
        "• Cart persists across page refreshes\n"
        "• Checkout button is disabled when cart is empty"
    ),
}

col_input, col_example = st.columns([3, 1])
with col_example:
    chosen = st.selectbox("Load example", list(example_stories.keys()), label_visibility="collapsed")

with col_input:
    pass  # spacer

story_value = example_stories.get(chosen, "") if chosen != "— pick an example —" else ""

user_story = st.text_area(
    "User story input",
    value=story_value,
    height=200,
    placeholder=(
        "Paste your user story, acceptance criteria, or Gherkin steps here…\n\n"
        "Example:\n"
        "Acceptance Criteria:\n"
        "- User can log in with email and password\n"
        "- Error shown on invalid credentials"
    ),
    label_visibility="collapsed",
)

# ── Generate button ───────────────────────────────────────────────────────────
generate_col, _ = st.columns([1, 2])
with generate_col:
    url_missing = not base_url or not base_url.strip()
if url_missing:
    st.markdown(
        '<div class="status-box warn">⚠ Enter the Application URL in the sidebar before generating.</div>',
        unsafe_allow_html=True,
    )
generate_clicked = st.button(
    "⚡ Generate Tests",
    type="primary",
    use_container_width=True,
    disabled=url_missing,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Run pipeline when button clicked ─────────────────────────────────────────
if generate_clicked:
    if not user_story.strip():
        st.markdown(
            '<div class="status-box error">⛔  Please paste a user story or acceptance criteria first.</div>',
            unsafe_allow_html=True,
        )
    else:
        mode_map = {
            "Smart (Recommended)": "smart",
            "Lightweight (Regex Only)": "lightweight",
            "Always Use LLM": "always_llm",
        }
        with st.spinner("Running pipeline…"):
            ok = run_generation(
                story=user_story,
                base_url=base_url,
                parse_mode=mode_map[parse_mode],
                model_name=model_name,
            )
        if not ok:
            st.error("Generation failed — see log below.")

# ── Live log ──────────────────────────────────────────────────────────────────
if st.session_state.generation_log:
    st.markdown('<span class="section-label">🖥 Pipeline Log</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="log-stream">{_render_log()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.generated_test:
    # Metrics row
    st.markdown(
        f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="val">{st.session_state.criteria_count}</div>
            <div class="lbl">Criteria Parsed</div>
        </div>
        <div class="metric-card">
            <div class="val">{st.session_state.generated_test.count(chr(10))}</div>
            <div class="lbl">Lines of Code</div>
        </div>
        <div class="metric-card">
            <div class="val">3</div>
            <div class="lbl">Report Formats</div>
        </div>
        <div class="metric-card">
            <div class="val" style="font-size:0.85rem;padding-top:0.3rem">{st.session_state.parse_method}</div>
            <div class="lbl">Parse Method</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Output tabs ──────────────────────────────────────────────────────────
    tab_test, tab_local, tab_jira, tab_html = st.tabs(
        [
            "🐍 generated_test.py",
            "📄 report_local.md",
            "🔵 report_jira.md",
            "🌐 report.html",
        ]
    )

    with tab_test:
        st.code(st.session_state.generated_test, language="python")

    with tab_local:
        st.markdown(st.session_state.report_local)

    with tab_jira:
        st.code(st.session_state.report_jira, language="markdown")
        st.caption("Copy this and paste directly into a Jira ticket description.")

    with tab_html:
        st.components.v1.html(
            st.session_state.report_html,
            height=500,
            scrolling=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">📦 Download</span>', unsafe_allow_html=True)

    dl1, dl2, dl3, dl4, dl5 = st.columns(5)

    bundle_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    with dl1:
        st.download_button(
            "⬇ test.py",
            data=st.session_state.generated_test,
            file_name="generated_test.py",
            mime="text/plain",
        )
    with dl2:
        st.download_button(
            "⬇ local.md",
            data=st.session_state.report_local,
            file_name="report_local.md",
            mime="text/markdown",
        )
    with dl3:
        st.download_button(
            "⬇ jira.md",
            data=st.session_state.report_jira,
            file_name="report_jira.md",
            mime="text/markdown",
        )
    with dl4:
        st.download_button(
            "⬇ report.html",
            data=st.session_state.report_html,
            file_name="report.html",
            mime="text/html",
        )
    with dl5:
        st.download_button(
            "⬇ bundle.zip",
            data=_build_zip(),
            file_name=f"evidence_bundle_{bundle_id}.zip",
            mime="application/zip",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="status-box">Last run: {st.session_state.last_run_time} · '
        f"Story: {st.session_state.last_story}</div>",
        unsafe_allow_html=True,
    )

elif not generate_clicked:
    # Empty state
    st.markdown(
        """
    <div style="text-align:center;padding:4rem 0;color:#2a3848">
        <div style="font-size:3rem;margin-bottom:1rem">🎭</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#3d5060">
            Paste a user story and click Generate
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;margin-top:0.5rem;color:#1e2e3a">
            supports: acceptance criteria · gherkin · bullet points · free-form text
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
