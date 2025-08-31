import anyio

from sentra_engine.agents.coordinator import CoordinatorAgent
from sentra_engine.agents.legal.use_case_contract_drafting import run_contract_drafting_agent
from sentra_engine.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra_engine.models import ConversationRequest


def _run_agent(agent_fn, request):
    async def _inner():
        events = []
        async for ev in agent_fn(request, {}):
            events.append(ev)
        return events

    return anyio.run(_inner)


def test_contract_drafting_agent_emits_three_events():
    request = ConversationRequest(messages=["Please draft a clause"])
    events = _run_agent(run_contract_drafting_agent, request)
    assert [e.type for e in events] == ["step_start", "message_delta", "step_end"]
    assert events[0].task_type == "contract_drafting"
    assert events[-1].task_type == "contract_drafting"


def test_listings_search_agent_emits_three_events():
    request = ConversationRequest(messages=["Find me apartment listings"])
    events = _run_agent(run_listings_search_agent, request)
    assert [e.type for e in events] == ["step_start", "message_delta", "step_end"]
    assert events[0].task_type == "listings_search"
    assert events[-1].task_type == "listings_search"


def _run_coordinator(message: str):
    request = ConversationRequest(messages=[message])
    agent = CoordinatorAgent()

    async def _inner():
        events = []
        async for ev in agent.run(request):
            events.append(ev)
        return events

    return anyio.run(_inner)


def test_coordinator_routes_to_use_case_agents():
    events = _run_coordinator("Can you draft this contract?")
    assert events[0].task_type == "contract_drafting"

    events = _run_coordinator("Show apartment listings in Madrid")
    assert events[0].task_type == "listings_search"
