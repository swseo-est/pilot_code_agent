import pytest
from unittest.mock import patch, MagicMock
from code_agent.graph.execution.nodes.message_append import message_append_node
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState

def make_state(assistant_id="asst_1", thread_id="thread_1", input_text="질문"):
    private = CodeExecutionPrivateState(
        assistant_id=assistant_id,
        thread_id=thread_id
    )
    return CodeExecutionState(
        user_input=UserInputState(input=input_text, user_id="u", session_id="s"),
        private=private
    )

@patch("code_agent.graph.execution.nodes.message_append.openai")
def test_message_append_success(mock_openai):
    # 메시지 생성 mock
    mock_message = MagicMock()
    mock_message.id = "msg_123"
    mock_openai.beta.threads.messages.create.return_value = mock_message

    state = make_state()
    result = message_append_node(state)

    assert result.private.message_id == "msg_123"
    mock_openai.beta.threads.messages.create.assert_called_once_with(
        thread_id="thread_1",
        role="user",
        content="질문"
    )

@patch("code_agent.graph.execution.nodes.message_append.openai")
def test_message_append_missing_ids(mock_openai):
    # assistant_id, thread_id가 없으면 예외 발생
    state = make_state(assistant_id=None, thread_id=None)
    with pytest.raises(ValueError):
        message_append_node(state) 