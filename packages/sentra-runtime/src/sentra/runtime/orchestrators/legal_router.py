from typing import Optional


def route_legal_intent(message: str) -> Optional[str]:
    """Route legal-related messages to the appropriate agent.

    Parameters
    ----------
    message: str
        Incoming user message.

    Returns
    -------
    Optional[str]
        ``"LegalDraftingAgent"`` if any legal keyword is present, otherwise ``None``.
    """
    keywords = ["lease", "contract", "agreement", "clause", "ndas"]
    if any(k in message.lower() for k in keywords):
        return "LegalDraftingAgent"
    return None
