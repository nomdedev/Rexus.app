"""
Pytest conftest to ensure repository root is on sys.path so legacy imports
like `src.modules...` resolve during tests regardless of pytest's cwd.

This is a small compatibility helper for the CI/test environment only.
"""
import os
import sys


def pytest_sessionstart(session):
    # Ensure the repository root (this file's directory) is first on sys.path
    repo_root = os.path.abspath(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
