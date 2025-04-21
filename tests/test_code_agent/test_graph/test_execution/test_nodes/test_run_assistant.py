import pytest
from unittest.mock import patch, MagicMock
from code_agent.graph.execution.nodes.run_assistant import run_assistant_node
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState
import asyncio
import tempfile
import yaml
from code_agent.graph.execution.nodes.entry_node import entry_node


@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.run_assistant.openai")
async def test_run_assistant_completed(mock_openai):
    # 정상 완료 케이스 (stream 방식)
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    class DummyStream:
        def __enter__(self):
            RunData = MagicMock()
            RunData.id = "run_123"
            RunData.status = "completed"
            RunData.object = "thread.run"
            event = MagicMock()
            event.data = RunData
            event.data.object = "thread.run"
            return iter([event])
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_client.beta.threads.runs.create.return_value = DummyStream()

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
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    class DummyStream:
        def __enter__(self):
            RunData = MagicMock()
            RunData.id = "run_456"
            RunData.status = "failed"
            RunData.object = "thread.run"
            event = MagicMock()
            event.data = RunData
            event.data.object = "thread.run"
            return iter([event])
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_client.beta.threads.runs.create.return_value = DummyStream()

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
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id="asst_3", thread_id="thread_3", message_id="msg_3", run_id="run_3"
        ),
        node_options={
            "run_assistant_node": {
                "timeout_sec": 5
            }
        }
    )
    # stream context manager에서 TimeoutError 발생
    class DummyStream:
        def __enter__(self):
            raise asyncio.TimeoutError()
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_client.beta.threads.runs.create.return_value = DummyStream()
    # cancel도 mock
    mock_client.beta.threads.runs.cancel = MagicMock()

    result = await run_assistant_node(state)
    assert result.private.run_status == "timeout"
    mock_client.beta.threads.runs.cancel.assert_called_once_with(
        thread_id="thread_3", run_id="run_3"
    )
    assert "실행을 취소했습니다" in result.private.error_msg

@pytest.mark.asyncio
async def test_run_assistant_missing_ids():
    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(
            assistant_id=None, thread_id=None, message_id=None
        )
    )
    with pytest.raises(ValueError):
        await run_assistant_node(state)


def test_entry_node_config_path_merge():
    # entry_node의 config_path 분기 및 merge 로직 커버
    config = {
        "run_assistant_node": {
            "timeout_sec": 123
        }
    }
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as tmp:
        yaml.dump(config, tmp)
        tmp.flush()
        state_dict = {
            "input": "테스트",
            "user_id": "u",
            "session_id": "s"
        }
        result = entry_node(state_dict, config_path=tmp.name)
        assert result.node_options["run_assistant_node"]["timeout_sec"] == 123 