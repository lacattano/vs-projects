"""
Test Case Base Class
Each individual test case should inherit from this class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestCaseResult:
    """Represents the result of running a test case"""

    test_case_id: str
    status: str  # "success", "failed", "error", "skipped"
    message: str
    execution_time_ms: float
    timestamp: datetime
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return {
            "test_case_id": self.test_case_id,
            "status": self.status,
            "message": self.message,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class TestCase(ABC):
    """Abstract base class for all test cases"""

    name: str = "BaseTestCase"
    description: str = "Base test case description"
    category: str = "general"
    priority: int = 1

    @classmethod
    def get_test_case_id(cls) -> str:
        """Generate a unique ID for this test case"""
        return f"{cls.__module__}.{cls.__name__}"

    @property
    def test_id(self) -> str:
        """Get the unique test ID"""
        return self.get_test_case_id()

    def setup(self, env_vars: dict | None = None) -> None:
        """Called before test execution"""
        pass

    def teardown(self, result: TestCaseResult) -> None:
        """Called after test execution"""
        pass

    @abstractmethod
    def execute(self, env_vars: dict | None = None) -> TestCaseResult:
        """Execute the test case and return the result"""
        pass

    @classmethod
    def get_metadata(cls) -> dict:
        """Get metadata about this test case"""
        return {
            "name": cls.name,
            "description": cls.description,
            "category": cls.category,
            "priority": cls.priority,
        }
