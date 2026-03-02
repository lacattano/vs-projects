import os
import re
from typing import Any

import requests


class LLMClient:
    def __init__(self, model_name: str | None = None):
        """
        Initialize the LLM Client with the specified model.
        Falls back to OLLAMA_MODEL environment variable or default.
        In CI environments (GitHub Actions), uses mock mode to generate test code.
        """
        self.url = "http://localhost:11434/api/generate"
        self._model = model_name or os.getenv("OLLAMA_MODEL", "qwen3.5:35b")
        self.user_prompt: str | None = None
        self.response: dict[str, Any] | None = None
        self._is_ci = os.getenv("GITHUB_ACTIONS") == "true" or bool(os.getenv("CI"))
        self.system_prompt: str = """You are an expert Playwright testing engineer.
        Your task is to generate clean, modern, and robust Playwright (Python) test code with screenshot capture for test evidence.
        Follow these rules:
        1. Import from `playwright.async_api import async_playwright, Page, expect`.
        2. Include comments explaining the steps.
        3. Return ONLY the code block inside triple backticks. Do not add explanations.
        4. Handle waits implicitly where possible, but use explicit waits for dynamic content.
        5. Use meaningful selector strategies (data-testid, CSS, XPath, get_by_role, get_by_label, etc.).
        6. The test should cover the specific scenario requested.
        7. IMPORTANT: Do NOT include `import pytest` - the test will be run directly as a Python script.
        8. IMPORTANT: Use async/await with async_playwright for the test execution.
        9. IMPORTANT: Test against URL http://localhost:8080 for the mock insurance site.
        10. The generated test must be runnable as a standalone script with: python test_filename.py.
        11. CAPTURE SCREENSHOTS for test evidence:
            - Take screenshot on test entry: screenshots/test_entry_YYYYMMDD_HHMMSS.png
            - Take screenshot after key interactions (form fills, button clicks): screenshots/step_description_YYYYMMDD_HHMMSS.png
            - Take screenshot on success condition is met: screenshots/test_passed_YYYYMMDD_HHMMSS.png
            - Playwright automatically captures screenshot on assertion failure in the console.
        12. Use try/except to capture screenshot on failure. The test must save screenshots to a 'screenshots/' subdirectory."""

    @property
    def model_name(self) -> str:
        """Return the current model name being used."""
        return self._model

    def generate_test(self, user_request: str, additional_context: dict | None = None) -> str:
        """
        Generate a test script based on a user request description.
        user_request: A string describing the test scenario.
        additional_context: A dictionary containing additional context (e.g., selectors, page URL).
        In CI environments, returns a pre-written Playwright test for the basic flow.
        """
        self.user_prompt = f"Scenario: {user_request}"
        if additional_context:
            self.user_prompt += f"\nAdditional Context: {additional_context}"

        if not user_request:
            raise ValueError("User request cannot be empty.")

        # Mock mode for CI environments
        if self._is_ci:
            print("CI environment detected. Using mock mode for test generation.")
            return self._generate_mock_test(user_request, additional_context)

        payload = {
            "model": self.model_name,
            "prompt": self.user_prompt,
            "system": self.system_prompt,
            "stream": False,
        }
        try:
            # Configurable timeout (default 60s, can be overridden via OLLAMA_TIMEOUT env var)
            timeout = int(os.getenv("OLLAMA_TIMEOUT", "60"))
            response = requests.post(self.url, json=payload, timeout=timeout)
            response.raise_for_status()
            self.response = response.json()
            if self.response:
                raw: str = self.response.get("response", "")
                return self._extract_code(raw)
            return ""
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("Could not connect to Ollama. Ensure it is running on port 11434.") from e
        except requests.exceptions.RequestException:
            print("Request failed")
            return ""
        except Exception:
            raise

    def _generate_mock_test(self, user_request: str, additional_context: dict | None = None) -> str:
        """
        Generate a mock test for CI environments.
        Returns a pre-written Playwright test that covers basic insurance site functionality.
        """
        mock_test_content = """import asyncio
from playwright.async_api import async_playwright, expect


async def main():
    \"\"\"
    Mock Playwright test for CI environment.
    This is a placeholder test that covers basic insurance site functionality.
    \"\"\"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto("http://localhost:8080")
        
        # Navigate to quote request page
        await page.get_by_role("link", name="Get a Quote").click()
        
        # Wait for and fill in the form
        await expect(page.get_by_role("heading", name="Get a Quote")).to_be_visible()
        
        # Fill in basic quote information
        await page.get_by_label("Postcode").fill("SW1A 1AA")
        await page.get_by_label("First Name").fill("John")
        await page.get_by_label("Last Name").fill("Doe")
        
        # Take screenshot of form
        await page.screenshot(path="screenshots/step_fill_quote_form.png")
        
        # Submit the form
        await page.get_by_role("button", name="Get Quote").click()
        
        # Wait for results
        await expect(page.get_by_text("Insurance Quotes")).to_be_visible()
        
        # Take screenshot of results
        await page.screenshot(path="screenshots/test_passed.png")
        
        await browser.close()
        print("Mock test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
"""
        return mock_test_content

    def _extract_code(self, text: str) -> str:
        """
        Extract the code block enclosed in triple backticks.
        Returns code content stripped of surrounding whitespace.
        If no markdown fences are found, returns the original text stripped.
        """
        pattern = r"```(?:python)?\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Strip trailing whitespace (including newline) before closing fences
            return match.group(1).rstrip()
        # Return original text stripped if no markdown fences found
        if text is None:
            return ""
        return text.strip()
