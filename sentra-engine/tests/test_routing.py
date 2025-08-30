from sentra_engine.policies import route_event


def test_route_event_returns_default() -> None:
    assert route_event(object()) == "default"
