import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# Import app - handling imports carefully
import sys
import os
from unittest.mock import MagicMock

# MOCK weasyprint to avoid OSError on mac if libraries are missing
# This must be done BEFORE importing modules that import weasyprint
sys.modules["weasyprint"] = MagicMock()
sys.modules["weasyprint.HTML"] = MagicMock()
sys.modules["weasyprint.CSS"] = MagicMock()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app

client = TestClient(app)

def test_chat_stream_endpoint():
    """Verify standard chat streaming flow with mocked agent."""
    
    # Hack: Reset the global memory_facade in server.main to avoid real DB init
    with patch("server.main.memory_facade", new=MagicMock()) as mock_memory:
        mock_memory.initialize = AsyncMock()
        mock_memory.get_context_for_planner = AsyncMock(return_value={})
        
        # Mock the DeepResearchAgent
        with patch("server.main.DeepResearchAgent") as MockAgentClass:
            mock_agent = MockAgentClass.return_value
            mock_agent._create_initial_state.return_value = {}
            
            # Create an async generator for astream
            async def mock_astream(*args, **kwargs):
                # 1. Log Event
                yield ((), "custom", {
                    "event_type": "agent_progress", 
                    "payload": {"status": "starting research"}
                })
                # 2. Token Event
                yield ((), "custom", {
                    "event_type": "response_token", 
                    "payload": {"token": "Hello"}
                })
                # 3. Interrupt Event
                # We need an object with a .value attribute, not a dict
                from types import SimpleNamespace
                interrupt_item = SimpleNamespace(value={"plan_display": "Plan A"})
                
                yield ((), "updates", {
                    "__interrupt__": [interrupt_item]
                })

            mock_agent._graph.astream = mock_astream

            # Make request
            response = client.post("/chat", json={
                "message": "Research AI",
                "user_id": "test_user"
            })
            
            assert response.status_code == 200
            
            content = response.text
            lines = [line for line in content.split('\n') if line.startswith("data: ")]
            events = [json.loads(line[6:]) for line in lines]
            
            # Verify Events
            event_types = [e["type"] for e in events]
            assert "thread_created" in event_types
            assert "log" in event_types
            assert "token" in event_types
            assert "interrupt" in event_types
            
            # Verify content
            token_event = next(e for e in events if e["type"] == "token")
            assert token_event["content"] == "Hello"
            
            log_event = next(e for e in events if e["type"] == "log")
            assert log_event["data"]["payload"]["status"] == "starting research"

def test_history_endpoint():
    """Verify history retrieval."""
    with patch("server.main.memory_facade") as mock_memory:
        # User AsyncMock for async methods
        mock_memory.short_term.get_conversation_history = AsyncMock(return_value=[
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"}
        ])
        
        response = client.get("/chat/th_123/history")
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == "th_123"
        assert len(data["messages"]) == 2
