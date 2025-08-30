import importlib
import pkgutil

def test_all_modules_import():
    """Import all sentra_engine submodules to catch syntax/import errors early."""
    package = importlib.import_module("sentra_engine")
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(name)
