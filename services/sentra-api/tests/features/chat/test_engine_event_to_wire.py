from sentra_brain_api.features.chat.mappers import engine_event_to_wire


def test_message_final_delivers_content():
    final_text = "Hello world!"
    evt = {"type": "message_final", "content": final_text}
    out = engine_event_to_wire(evt)
    assert out.type == "message_final"
    assert out.content == final_text
