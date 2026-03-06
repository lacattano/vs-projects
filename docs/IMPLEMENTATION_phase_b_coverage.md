# Phase B — Test Map & Coverage

**Feature:** Save, Review & Run Workflow  
**Status:** Ready for implementation  
**Backlog items:** B-003

---

## Objective

- Parse generated tests to extract test functions
- Map each test to the requirement criterion that generated it
- Display coverage percentage and show which criteria have tests
- Provide a visual map of requirements → tests

---

## Data Structures

### `TestFunction` NamedTuple

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TestFunction:
    name: str
    start_line: int
    end_line: int
    source_lines: list[str]
    criterion_id: Optional[str] = None
    criterion_text: Optional[str] = None
```

### `RequirementCoverage` NamedTuple

```python
from dataclasses import dataclass

@dataclass
class RequirementCoverage:
    criterion_id: str
    criterion_text: str
    test_name: Optional[str] = None
    has_test: bool = False
```

---

## Helper Functions

### 1. `parse_test_file(file_path: str) -> list[TestFunction]`

Extracts test functions from a generated test file.

**Implementation:**
```python
import ast
from typing import Iterator

def parse_test_file(file_path: str) -> list[TestFunction]:
    """
    Parse a test file and extract test functions.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        List of TestFunction namedtuples
    """
    from pathlib import Path
    
    source = Path(file_path).read_text(encoding="utf-8")
    lines = source.splitlines()
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in test file: {e}")
    
    test_functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if it's a test function (starts with test_)
            if node.name.startswith("test_"):
                # Get source lines
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line
                source_lines = lines[start_line - 1:end_line]
                
                test_functions.append(TestFunction(
                    name=node.name,
                    start_line=start_line,
                    end_line=end_line,
                    source_lines=source_lines
                ))
    
    return test_functions
```

---

### 2. `map_tests_to_criteria(criteria_list: list[dict], test_functions: list[TestFunction]) -> list[RequirementCoverage]`

Maps generated tests to the original requirement criteria.

**Strategy:**
- Match `test_` prefix to requirement IDs (e.g., `test_1_login_flow` → requirement 1)
- If no direct match, use heuristic matching (keyword matching)

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TestFunction:
    name: str
    start_line: int
    end_line: int
    source_lines: list[str]
    criterion_id: Optional[str] = None
    criterion_text: Optional[str] = None

@dataclass
class RequirementCoverage:
    criterion_id: str
    criterion_text: str
    test_name: Optional[str] = None
    has_test: bool = False
    matched_by: str = field(default="heuristic")

def map_tests_to_criteria(criteria_list: list[dict], test_functions: list[TestFunction]) -> list[RequirementCoverage]:
    """
    Map test functions to requirement criteria.
    
    Strategy:
    1. Try direct ID match (e.g., test_1_something → criterion 1)
    2. Fallback to heuristic keyword matching
    
    Args:
        criteria_list: List of parsed criteria from prompt
        test_functions: List of parsed test functions
        
    Returns:
        List of RequirementCoverage with matching status
    """
    coverage = []
    
    for criterion in criteria_list:
        criterion_id = criterion.get("id", "")
        criterion_text = criterion.get("text", "")
        
        matched_test = None
        
        # Strategy 1: Direct ID match
        # e.g., test_1_login_flow → criterion 1
        for test in test_functions:
            test_parts = test.name.split("_")
            if len(test_parts) > 1 and test_parts[1].isdigit():
                test_id = test_parts[1]
                if test_id == criterion_id:
                    matched_test = test
                    matched_by = "direct"
                    break
        
        # Strategy 2: Heuristic matching
        if not matched_test:
            criterion_keywords = set(criterion_text.lower().split())
            best_match = None
            best_score = 0
            
            for test in test_functions:
                test_source = " ".join(test.source_lines).lower()
                test_name = test.name.lower()
                
                # Score based on keyword overlap
                score = 0
                for keyword in criterion_keywords:
                    if len(keyword) > 3 and keyword in test_source:
                        score += 1
                    if len(keyword) > 3 and keyword in test_name:
                        score += 1
                
                if score > best_score:
                    best_score = score
                    best_match = test
            
            if best_match and best_score > 0:
                matched_test = best_match
                matched_by = "heuristic"
        
        coverage.append(RequirementCoverage(
            criterion_id=criterion_id,
            criterion_text=criterion_text,
            test_name=matched_test.name if matched_test else None,
            has_test=matched_test is not None,
            matched_by=matched_by
        ))
    
    return coverage
```

---

### 3. `calculate_coverage(coverage_list: list[RequirementCoverage]) -> dict`

Calculates coverage statistics.

**Implementation:**
```python
def calculate_coverage(coverage_list: list[RequirementCoverage]) -> dict:
    """
    Calculate coverage statistics.
    
    Args:
        coverage_list: List of RequirementCoverage
        
    Returns:
        Dict with coverage statistics
    """
    total = len(coverage_list)
    covered = sum(1 for c in coverage_list if c.has_test)
    
    coverage_pct = (covered / total * 100) if total > 0 else 0
    
    return {
        "total_criteria": total,
        "covered_criteria": covered,
        "uncovered_criteria": total - covered,
        "coverage_percentage": round(coverage_pct, 1)
    }
```

---

### 4. `extract_criteria_from_prompt(prompt_text: str) -> list[dict]`

Parses requirement criteria from the original prompt.

**Assumes criteria are numbered or bulleted in the prompt.**

**Implementation:**
```python
import re
from typing import list, dict

def extract_criteria_from_prompt(prompt_text: str) -> list[dict]:
    """
    Extract numbered/bulleted criteria from prompt.
    
    Expected format examples:
    - "1. Login should work with valid credentials"
    - "2. Logout should clear session"
    - "- Feature A should do X"
    - "• Feature B should do Y"
    
    Args:
        prompt_text: The original user prompt
        
    Returns:
        List of dicts with 'id' and 'text' keys
    """
    criteria = []
    
    # Pattern for numbered items: "1.", "2.", etc.
    numbered_pattern = r'^(\d+)\.\s+(.+)$'
    
    # Pattern for bullet items: "-", "*",
    bullet_pattern = r'^[\-\•]\s+(.+)$'
    
    lines = prompt_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Try numbered match
        match = re.match(numbered_pattern, line)
        if match:
            criteria.append({
                "id": match.group(1),
                "text": match.group(2)
            })
            continue
        
        # Try bullet match
        match = re.match(bullet_pattern, line)
        if match:
            # Generate numeric ID for bullets
            criteria.append({
                "id": str(len(criteria) + 1),
                "text": match.group(1)
            })
            continue
    
    return criteria
```

---

## UI Changes in `streamlit_app.py`

### Coverage Display Component

```python
def display_coverage(coverage_list: list[RequirementCoverage], stats: dict):
    """
    Display test coverage breakdown in UI.
    """
    st.markdown("### 📊 Test Coverage")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Criteria", stats["total_criteria"])
    with col2:
        st.metric("Covered", stats["covered_criteria"])
    with col3:
        st.metric("Coverage", f"{stats['coverage_percentage']}%")
    
    # Coverage progress bar
    st.progress(stats["coverage_percentage"] / 100)
    
    # Detailed coverage list
    st.markdown("#### Coverage Details")
    
    for req in coverage_list:
        icon = "✅" if req.has_test else "❌"
        status = f"✅ Test: {req.test_name}" if req.has_test else "❌ Not tested"
        
        with st.expander(f"{icon} Requirement {req.criterion_id}: {req.criterion_text[:50]}..."):
            st.write(f"**Status:** {status}")
            if req.test_name:
                st.write(f"**Matched by:** {req.matched_by}")
            st.write(f"**Full text:** {req.criterion_text}")
```

---

### Integration Flow

**After test generation:**

```python
# 1. Generate test (existing)
test_code = generate_test_for_story(prompt_text, base_url, llm_client)

# 2. Save test (Phase A)
saved_path = save_generated_test(test_code, base_url)

# 3. Parse saved test
try:
    test_functions = parse_test_file(saved_path)
except ValueError as e:
    st.error(f"Failed to parse test file: {e}")
    test_functions = []

# 4. Extract criteria from original prompt
criteria_list = extract_criteria_from_prompt(prompt_text)

# 5. Map tests to criteria
coverage_list = map_tests_to_criteria(criteria_list, test_functions)

# 6. Calculate coverage stats
coverage_stats = calculate_coverage(coverage_list)

# 7. Display coverage
display_coverage(coverage_list, coverage_stats)
```

---

## Error Handling

| Scenario | Response |
|------|------|
| Test file has syntax errors | Show error: "Failed to parse test file: {error}. Please review the generated code." |
| No criteria extracted from prompt | Show warning: "Could not extract criteria from prompt. Coverage mapping unavailable." |
| Empty test file | Show warning: "Test file is empty. No tests to analyze." |
| No tests found in file | Show warning: "No test functions found in the generated test." |

---

## Testing Phase B

### Unit tests (tests/test_phase_b_helpers.py):

```python
import pytest
from streamlit_app import (
    parse_test_file,
    map_tests_to_criteria,
    calculate_coverage,
    extract_criteria_from_prompt,
    TestFunction,
    RequirementCoverage
)

def test_extract_criteria_from_prompt_numbered():
    prompt = """
    1. Login should work with valid credentials
    2. Logout should clear session
    3. Error message should appear for invalid login
    """
    criteria = extract_criteria_from_prompt(prompt)
    
    assert len(criteria) == 3
    assert criteria[0]["id"] == "1"
    assert "Login" in criteria[0]["text"]
    assert criteria[1]["id"] == "2"

def test_extract_criteria_from_prompt_bullets():
    prompt = """
    - Feature A should do X
    - Feature B should do Y
    """
    criteria = extract_criteria_from_prompt(prompt)
    
    assert len(criteria) == 2
    assert criteria[0]["id"] == "1"
    assert criteria[1]["id"] == "2"

def test_map_tests_to_criteria_direct():
    criteria = [
        {"id": "1", "text": "User should be able to login"},
        {"id": "2", "text": "User should be able to logout"}
    ]
    
    test_functions = [
        TestFunction(name="test_1_login_flow", start_line=10, end_line=20, source_lines=["def test_1_login_flow():"]),
        TestFunction(name="test_2_logout_flow", start_line=25, end_line=35, source_lines=["def test_2_logout_flow():"])
    ]
    
    coverage = map_tests_to_criteria(criteria, test_functions)
    
    assert len(coverage) == 2
    assert coverage[0].has_test
    assert coverage[0].test_name == "test_1_login_flow"
    assert coverage[1].has_test
    assert coverage[1].test_name == "test_2_logout_flow"

def test_calculate_coverage():
    coverage = [
        RequirementCoverage("1", "Test 1", "test_1", True),
        RequirementCoverage("2", "Test 2", "test_2", True),
        RequirementCoverage("3", "Test 3", None, False)
    ]
    
    stats = calculate_coverage(coverage)
    
    assert stats["total_criteria"] == 3
    assert stats["covered_criteria"] == 2
    assert stats["coverage_percentage"] == 66.7
```

---

## Integration Checklist

- [ ] Add `TestFunction` and `RequirementCoverage` dataclasses to `streamlit_app.py`
- [ ] Add `parse_test_file()` helper function to `streamlit_app.py`
- [ ] Add `map_tests_to_criteria()` helper function to `streamlit_app.py`
- [ ] Add `calculate_coverage()` helper function to `streamlit_app.py`
- [ ] Add `extract_criteria_from_prompt()` helper function to `streamlit_app.py`
- [ ] Add `display_coverage()` UI component to `streamlit_app.py`
- [ ] Integrate coverage display after test generation
- [ ] Add error handling for parsing failures
- [ ] Add unit tests for helper functions

---

## Next Steps

Once Phase B is complete:
1. Verify criteria extraction works for various prompt formats
2. Verify test mapping accuracy (direct and heuristic)
3. Verify coverage percentage calculation
4. Proceed to Phase C (Run Now)

---

**End of Phase B Implementation Document**