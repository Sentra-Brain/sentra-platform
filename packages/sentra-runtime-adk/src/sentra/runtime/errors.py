class ToolError(Exception):
    """Raised when a tool invocation fails."""


class TimeoutError(Exception):
    """Raised when an operation times out."""


class BudgetExhaustedError(Exception):
    """Raised when the execution budget is exhausted."""
