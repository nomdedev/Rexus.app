"""Compatibility shim: redirect imports from `src.*` to `rexus.*`.

This module installs a meta path finder that maps any import starting with
`src.` to the corresponding `rexus.` module. It keeps a thin loader that
imports the target and copies its namespace into the requested module name.

This is a non-invasive compatibility shim to allow legacy tests/scripts
that import `src.*` to work without modifying many files.
"""
import sys
import importlib
import importlib.util
import importlib.abc
import importlib.machinery


class _SrcToRexusLoader(importlib.abc.Loader):
    def __init__(self, target_name):
        self._target = target_name

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        # Import the real module and copy its attributes
        real = importlib.import_module(self._target)
        module.__dict__.clear()
        module.__dict__.update(real.__dict__)


class _SrcToRexusFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("src."):
            return None
        # Map src.foo.bar -> rexus.foo.bar
        target = "rexus." + fullname[4:]
        spec = importlib.util.find_spec(target)
        if spec is None:
            return None
        # Return a new spec that uses our loader but keeps package flag
        is_pkg = spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(fullname, _SrcToRexusLoader(target), is_package=is_pkg)


# Register our finder at highest priority if not already present
for f in sys.meta_path:
    if isinstance(f, _SrcToRexusFinder):
        break
else:
    sys.meta_path.insert(0, _SrcToRexusFinder())
