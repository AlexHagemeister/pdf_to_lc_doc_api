"""
Pytest configuration file.
"""

import warnings
import pytest


def pytest_configure(config):
    """Configure pytest."""
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module=".*swigvarlink.*"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module=".*SwigPyPacked.*"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module=".*SwigPyObject.*"
    )
