"""Local shim for google.adk used only in tests.

This module provides the `adk` subpackage so tests that import
`google.adk.sessions.DatabaseSessionService` don't fail during
collection. It intentionally defines minimal symbols.
"""

__path__ = __path__
