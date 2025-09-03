import asyncio
from sentra_engine import run_conversation
from sentra_engine.models import ConversationRequest

async def main():
    request = ConversationRequest(messages=["Search for available apartments."])
    async for event in run_conversation(request):
        print(f"[{event.type}] {event.content}")

if __name__ == "__main__":
    asyncio.run(main())
