from typing import Optional


def route_real_estate_intent(message: str) -> Optional[str]:
    """Route real-estate related messages to the appropriate agent.

    Parameters
    ----------
    message: str
        Incoming user message.

    Returns
    -------
    Optional[str]
        ``"ListingsSearchAgent"`` if any real-estate keyword is present, otherwise ``None``.
    """
    keywords = ["flat", "apartment", "listing", "square meters", "neighborhood"]
    if any(k in message.lower() for k in keywords):
        return "ListingsSearchAgent"
    return None
