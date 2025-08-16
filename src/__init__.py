"""Legacy compatibility removed.

This file previously provided a meta path finder to map `src.*` imports to
`rexus.*` during a migration. The project now uses a proper editable install
workflow (see `pyproject.toml`). Remove legacy imports and use `rexus.*` or
install the package in editable mode:

    python -m pip install -e .

If you still need temporary compatibility, add a focused shim with a clear
expiration and a test to ensure parity.
"""

__all__ = []
