import pytest
from unittest.mock import patch, MagicMock
from code_agent.graph.execution.nodes.run_assistant import run_assistant_node
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState
import asyncio


@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.run_assistant.openai")
async def test_run_assistant_completed(mock_openai):
    # 정상 완료 케이스
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.id = "run_123"
    mock_run.status = "completed"
    mock_client.beta.threads.runs.create_and_poll = MagicMock(return_value=mock_run)
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id="asst_1", thread_id="thread_1", message_id="msg_1"
        )
    )
    result = await run_assistant_node(state)
    assert result.private.run_id == "run_123"
    assert result.private.run_status == "completed"
    assert not getattr(result.private, "error_msg", None)

@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.run_assistant.openai")
async def test_run_assistant_not_completed(mock_openai):
    # run.status가 completed가 아닐 때
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.id = "run_456"
    mock_run.status = "failed"
    mock_client.beta.threads.runs.create_and_poll = MagicMock(return_value=mock_run)
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id="asst_2", thread_id="thread_2", message_id="msg_2"
        )
    )
    result = await run_assistant_node(state)
    assert result.private.run_id == "run_456"
    assert result.private.run_status == "failed"
    assert "정상적으로 완료되지 않았습니다" in result.private.error_msg

@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.run_assistant.openai")
async def test_run_assistant_timeout(mock_openai):
    # Timeout 발생 시
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id="asst_3", thread_id="thread_3", message_id="msg_3"
        )
    )
    with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
        result = await run_assistant_node(state, timeout_sec=5)
        assert result.private.run_status == "timeout"
        assert "timed out" in result.private.error_msg

@pytest.mark.asyncio
async def test_run_assistant_missing_ids():
    # 필수 ID 누락 시 예외 발생
    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id=None, thread_id=None, message_id=None
        )
    )
    with pytest.raises(ValueError):
        await run_assistant_node(state) 