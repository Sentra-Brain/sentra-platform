from sentra.runtime.orchestrators.legal_router import route_legal_intent
from sentra.runtime.orchestrators.real_estate_router import route_real_estate_intent


def test_route_legal_intent():
    assert route_legal_intent("Can you draft a lease agreement?") == "LegalDraftingAgent"
    assert route_legal_intent("Is this contract clause enforceable?") == "LegalDraftingAgent"
    assert route_legal_intent("Tell me about real estate") is None


def test_route_real_estate_intent():
    assert route_real_estate_intent("Show me apartment listings in Madrid") == "ListingsSearchAgent"
    assert route_real_estate_intent("Any flat available in Paris?") == "ListingsSearchAgent"
    assert route_real_estate_intent("What is a contract?") is None
