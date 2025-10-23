"""Test-only package namespace for google.* imports used by tests.

This package is a local shim that only exists to make import-time
dependencies available during the test run. It should not be used in
production code outside the test environment.
"""

__path__ = __path__  # namespace package
