import pytest
from unittest.mock import patch, MagicMock
from code_agent.graph.execution.nodes.extract_result import extract_result_node
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState

@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.extract_result.openai")
async def test_extract_result_success(mock_openai):
    # 정상 JSON 파싱
    json_str = '{"code": "print(1)", "explanation": "테스트", "result": "1"}'
    mock_message = MagicMock()
    mock_message.run_id = "run_1"
    mock_message.role = "assistant"
    mock_message.content = [MagicMock(text=MagicMock(value=json_str))]
    mock_messages = MagicMock()
    mock_messages.data = [mock_message]
    mock_client = MagicMock()
    mock_client.beta.threads.messages.list.return_value = mock_messages
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(thread_id="thread_1", run_id="run_1")
    )
    result = await extract_result_node(state)
    assert result.private.executed_code == "print(1)"
    assert result.private.explanation == "테스트"
    assert result.private.execution_result == "1"
    assert result.private.run_status is None

@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.extract_result.openai")
async def test_extract_result_parsing_failed(mock_openai):
    # JSON 파싱 실패
    bad_json_str = "{code: print(1), explanation: 테스트, result: 1}"  # 잘못된 JSON
    mock_message = MagicMock()
    mock_message.run_id = "run_2"
    mock_message.role = "assistant"
    mock_message.content = [MagicMock(text=MagicMock(value=bad_json_str))]
    mock_messages = MagicMock()
    mock_messages.data = [mock_message]
    mock_client = MagicMock()
    mock_client.beta.threads.messages.list.return_value = mock_messages
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(thread_id="thread_2", run_id="run_2")
    )
    result = await extract_result_node(state)
    assert result.private.run_status == "parsing_failed"
    assert result.private.error_msg == "결과 파싱에 실패했습니다."
    assert result.private.executed_code is None

@pytest.mark.asyncio
@patch("code_agent.graph.execution.nodes.extract_result.openai")
async def test_extract_result_no_message(mock_openai):
    # 메시지가 아예 없는 경우
    mock_messages = MagicMock()
    mock_messages.data = []
    mock_client = MagicMock()
    mock_client.beta.threads.messages.list.return_value = mock_messages
    mock_openai.OpenAI.return_value = mock_client

    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(thread_id="thread_3", run_id="run_3")
    )
    result = await extract_result_node(state)
    assert result.private.run_status == "no_message"
    assert result.private.error_msg == "assistant 메시지가 반환되지 않았습니다."
    assert result.private.executed_code is None

@pytest.mark.asyncio
async def test_extract_result_missing_ids():
    # 필수 ID 누락 시 예외 발생
    state = CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=CodeExecutionPrivateState(thread_id=None, run_id=None)
    )
    with pytest.raises(ValueError):
        await extract_result_node(state) 