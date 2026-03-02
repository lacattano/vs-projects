"""
Test Case Manager
Manages loading, discovering, and executing multiple test cases
"""

import importlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .test_case import TestCase, TestCaseResult

logger = logging.getLogger(__name__)


@dataclass
class TestSuiteResult:
    """Aggregated results from running multiple test cases"""

    total_test_cases: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_execution_time_ms: float
    test_results: list[TestCaseResult]
    timestamp: datetime

    def summary(self) -> dict:
        return {
            "total": self.total_test_cases,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "skipped": self.skipped,
            "pass_rate": f"{(self.passed / self.total_test_cases * 100):.1f}%" if self.total_test_cases > 0 else "0%",
            "total_time_ms": self.total_execution_time_ms,
            "test_results": [r.to_dict() for r in self.test_results],
        }


class TestCaseManager:
    """Manages a collection of test cases"""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.test_cases: list[TestCase] = []
        self._loaded_modules: set = set()
        self._discover_dir = Path(__file__).parent / "test_cases"

    def discover_test_cases(self) -> list[type[TestCase]]:
        """Discover all test cases in the test_cases directory"""
        discovered: list[type[TestCase]] = []

        if not self._discover_dir.exists():
            logger.warning(f"Test cases directory not found: {self._discover_dir}")
            return discovered

        for py_file in self._discover_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            module_name = f"src.test_cases.{py_file.stem}"
            try:
                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, TestCase) and attr is not TestCase:
                        discovered.append(attr)

                self._loaded_modules.add(module_name)

            except ImportError as e:
                logger.error(f"Failed to import {module_name}: {e}")
            except Exception as e:
                logger.error(f"Error processing {module_name}: {e}")

        return discovered

    def add_test_case(self, test_case: TestCase) -> None:
        """Manually add a test case instance"""
        self.test_cases.append(test_case)
        logger.info(f"Added test case: {test_case.test_id}")

    def add_test_case_from_class(self, test_class: type[TestCase]) -> None:
        """Add a test case from its class (creates instance)"""
        try:
            instance = test_class()
            self.add_test_case(instance)
        except Exception as e:
            logger.error(f"Failed to instantiate {test_class.__name__}: {e}")

    def clear_test_cases(self) -> None:
        """Clear all registered test cases"""
        self.test_cases.clear()
        logger.info("Cleared all test cases")

    def get_test_cases(self) -> list[TestCase]:
        """Get all registered test cases"""
        return self.test_cases

    def get_test_case_by_id(self, test_id: str) -> TestCase | None:
        """Get a specific test case by its ID"""
        for test_case in self.test_cases:
            if test_case.test_id == test_id:
                return test_case
        return None

    def run_test_case(self, test_case: TestCase, env_vars: dict | None = None) -> TestCaseResult:
        """Execute a single test case"""
        logger.info(f"Running test case: {test_case.test_id}")

        try:
            test_case.setup(env_vars)
            result = test_case.execute(env_vars)
            test_case.teardown(result)

            logger.info(f"Test case completed: {test_case.test_id} - {result.status}")
            return result

        except Exception as e:
            logger.error(f"Error running test case {test_case.test_id}: {e}")
            return TestCaseResult(
                test_case_id=test_case.test_id,
                status="error",
                message=f"Execution error: {str(e)}",
                execution_time_ms=0,
                timestamp=datetime.now(),
                metadata={"exception": type(e).__name__},
            )

    def run_test_suite(self, env_vars: dict | None = None) -> TestSuiteResult:
        """Run all registered test cases as a suite"""
        import time

        start_time = time.time()
        results: list[TestCaseResult] = []

        for test_case in self.test_cases:
            result = self.run_test_case(test_case, env_vars)
            results.append(result)

        total_time = (time.time() - start_time) * 1000

        passed = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")
        errors = sum(1 for r in results if r.status == "error")
        skipped = sum(1 for r in results if r.status == "skipped")

        return TestSuiteResult(
            total_test_cases=len(self.test_cases),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            total_execution_time_ms=total_time,
            test_results=results,
            timestamp=datetime.now(),
        )
