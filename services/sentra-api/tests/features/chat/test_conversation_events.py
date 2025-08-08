import pytest
import json
from unittest.mock import Mock
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent


class TestConversationEvents:
    
    def test_conversation_event_creation(self):
        """Test ConversationEvent model creation and serialization"""
        # Test step_start event
        step_event = ConversationEvent(
            type="step_start",
            step_id="rag_search",
            label="Searching knowledge base",
            status="running"
        )
        assert step_event.type == "step_start"
        assert step_event.step_id == "rag_search"
        assert step_event.label == "Searching knowledge base"
        assert step_event.status == "running"
        assert step_event.timestamp is not None
        
        # Test message_delta event
        delta_event = ConversationEvent(
            type="message_delta",
            content="Hello "
        )
        assert delta_event.type == "message_delta"
        assert delta_event.content == "Hello "
        assert delta_event.step_id is None
        
        # Test message_final event
        final_event = ConversationEvent(
            type="message_final",
            content="Hello world!"
        )
        assert final_event.type == "message_final"
        assert final_event.content == "Hello world!"
        
    def test_conversation_event_serialization(self):
        """Test ConversationEvent JSON serialization for SSE"""
        event = ConversationEvent(
            type="step_end",
            step_id="rag_search", 
            status="done",
            meta={"num_chunks": 5}
        )
        
        json_str = event.model_dump_json()
        parsed = json.loads(json_str)
        
        assert parsed["type"] == "step_end"
        assert parsed["step_id"] == "rag_search"
        assert parsed["status"] == "done"
        assert parsed["meta"]["num_chunks"] == 5
        assert "timestamp" in parsed
    
    def test_conversation_event_type_validation(self):
        """Test that ConversationEvent validates event types"""
        # Valid types should work
        valid_types = ["message_delta", "message_final", "step_start", "step_progress", "step_end", "step_error"]
        for event_type in valid_types:
            event = ConversationEvent(type=event_type, content="test")
            assert event.type == event_type
        
        # Invalid type should raise validation error
        with pytest.raises(ValueError):
            ConversationEvent(type="invalid_type", content="test")
    
    def test_conversation_event_sse_format(self):
        """Test that ConversationEvent produces proper SSE format"""
        event = ConversationEvent(
            type="step_start",
            step_id="rag_search",
            label="Searching knowledge base", 
            status="running"
        )
        
        # Simulate SSE formatting
        sse_line = f"data: {event.model_dump_json()}\n\n"
        
        # Should be parseable back
        json_part = sse_line.replace("data: ", "").strip()
        parsed = json.loads(json_part)
        
        assert parsed["type"] == "step_start"
        assert parsed["step_id"] == "rag_search"
        assert parsed["label"] == "Searching knowledge base"
        assert parsed["status"] == "running"