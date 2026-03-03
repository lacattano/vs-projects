"""
Configuration management for AI Playwright Test Generator.

This module provides centralized configuration for:
- LLM settings (model, detection mode, timeout)
- Test execution settings (framework, parallel execution, screenshot capture)
- Report settings (format types, link types)
- Screenshot settings (storage, naming convention)
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DetectionMode(Enum):
    """How to detect input format."""
    AUTO = "auto"           # Regex-first, LLM fallback
    EXPLICIT = "explicit"   # User specifies format
    FAST = "fast"           # Pure regex, no LLM
    THOROUGH = "thorough"   # LLM-based detection


class AnalysisMode(Enum):
    """How to analyze user stories."""
    FAST = "fast"           # Regex-based, no LLM
    THOROUGH = "thorough"   # LLM-powered
    AUTO = "auto"           # Fast first, thorough if complex


class CaptureLevel(Enum):
    """Level of screenshot capture."""
    BASIC = "basic"         # Entry and outcome only
    STANDARD = "standard"   # Entry, steps, outcome
    THOROUGH = "thorough"   # Every major action


class ReportFormat(Enum):
    """Report output format."""
    CONFLUENCE = "confluence"    # HTML for Confluence/Cloud
    JIRA_XML = "jira_xml"        # XML for Jira import
    JSON = "json"                # JSON data format
    MARKDOWN = "markdown"        # Markdown documentation
    LOCAL = "local"              # Relative paths, for local viewing
    JIRA = "jira"                # Absolute paths, for Jira uploads
    SHAREABLE = "shareable"      # Clean, for team documentation

# Jira project configuration - can be overridden via environment variable
JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "TEST")


class ScreenshotNaming(Enum):
    """Screenshot naming convention."""
    SEQUENTIAL = "sequential"      # test_entry_001.png
    DESCRIPTIVE = "descriptive"    # login_success_20260303.png
    HYBRID = "hybrid"              # login_success_001_20260303.png


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # LLM Settings
    LLM_MODEL: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3.5:35b"))
    LLM_DETECTION_MODE: DetectionMode = field(default=DetectionMode.AUTO)
    LLM_ANALYSIS_MODE: AnalysisMode = field(default=AnalysisMode.AUTO)
    LLM_TIMEOUT: int = field(default=120)
    
    # Test Execution Settings
    TEST_FRAMEWORK: str = "pytest"
    PARALLEL_EXECUTION: bool = False
    CAPTURE_LEVEL: CaptureLevel = field(default=CaptureLevel.STANDARD)
    
    # Report Settings
    GENERATE_ALL_REPORTS: bool = True
    DEFAULT_REPORT_FORMAT: ReportFormat = field(default=ReportFormat.LOCAL)
    REPORT_LINK_TYPE: str = "relative"  # relative, absolute, both
    
    # Screenshot Settings
    SCREENSHOT_DIR: str = "screenshots"
    NAMING_CONVENTION: ScreenshotNaming = field(default=ScreenshotNaming.DESCRIPTIVE)
    STORAGE_MODE: str = "organized"  # organized, flatten, absolute_paths
    
    # Paths
    GENERATED_TESTS_DIR: str = "generated_tests"
    EVIDENCE_DIR: str = "evidence"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        config = cls()
        
        # LLM configuration
        ollama_model = os.getenv("OLLAMA_MODEL")
        if ollama_model:
            config.LLM_MODEL = ollama_model
        
        detection_mode = os.getenv("AI_PLAYWRIGHT_DETECTION_MODE", "auto")
        config.LLM_DETECTION_MODE = DetectionMode(detection_mode)
        
        analysis_mode = os.getenv("AI_PLAYWRIGHT_ANALYSIS_MODE", "auto")
        config.LLM_ANALYSIS_MODE = AnalysisMode(analysis_mode)
        
        timeout = os.getenv("OLLAMA_TIMEOUT")
        if timeout:
            config.LLM_TIMEOUT = int(timeout)
        
        # Test execution
        parallel = os.getenv("AI_PLAYWRIGHT_PARALLEL", "false").lower() == "true"
        config.PARALLEL_EXECUTION = parallel
        
        capture_level = os.getenv("AI_PLAYWRIGHT_CAPTURE_LEVEL", "standard")
        try:
            config.CAPTURE_LEVEL = CaptureLevel(capture_level)
        except ValueError:
            config.CAPTURE_LEVEL = CaptureLevel.STANDARD
        
        # Report settings
        if os.getenv("AI_PLAYWRIGHT_GENERATE_ALL_REPORTS", "true").lower() == "true":
            config.GENERATE_ALL_REPORTS = True
        
        report_format = os.getenv("AI_PLAYWRIGHT_REPORT_FORMAT", "local")
        try:
            config.DEFAULT_REPORT_FORMAT = ReportFormat(report_format)
        except ValueError:
            config.DEFAULT_REPORT_FORMAT = ReportFormat.LOCAL
        
        # Screenshot settings
        screenshot_dir = os.getenv("AI_PLAYWRIGHT_SCREENSHOT_DIR")
        if screenshot_dir:
            config.SCREENSHOT_DIR = screenshot_dir
        
        naming = os.getenv("AI_PLAYWRIGHT_NAMING_CONVENTION", "descriptive")
        try:
            config.NAMING_CONVENTION = ScreenshotNaming(naming)
        except ValueError:
            config.NAMING_CONVENTION = ScreenshotNaming.DESCRIPTIVE
        
        return config
    
    def __str__(self) -> str:
        """String representation for logging."""
        return (
            f"Config[LLM={self.LLM_MODEL}, detection={self.LLM_DETECTION_MODE.value}, "
            f"analysis={self.LLM_ANALYSIS_MODE.value}, timeout={self.LLM_TIMEOUT}s, "
            f"parallel={self.PARALLEL_EXECUTION}, screenshots={self.SCREENSHOT_DIR}, "
            f"reports=all:{self.GENERATE_ALL_REPORTS}]"
        )


# Global configuration instance
config: AppConfig = AppConfig()