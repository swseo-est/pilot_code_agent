import pytest
from unittest.mock import patch, MagicMock
from code_agent.graph.execution.nodes.thread_manager import thread_manager_node, create_openai_assistant
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState
import openai
from dotenv import load_dotenv
import time
from code_agent.graph.execution.nodes import thread_manager
from code_agent.graph.execution.nodes.entry_node import entry_node


def make_state(assistant_id=None, thread_id=None):
    # state dict에 private 필드로 assistant_id, thread_id를 포함
    state_dict = {
        "input": "테스트",
        "user_id": "u",
        "session_id": "s",
        # 아래는 CodeExecutionPrivateState의 필드명과 일치해야 함
        "assistant_id": assistant_id,
        "thread_id": thread_id,
    }
    return entry_node(state_dict)

@patch("code_agent.graph.execution.nodes.thread_manager.create_openai_assistant")
@patch("code_agent.graph.execution.nodes.thread_manager.openai")
def test_both_ids_missing(mock_openai, mock_create_assistant):
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    # assistant_id, thread_id 모두 없는 경우
    mock_create_assistant.return_value = "asst_123"
    mock_thread = MagicMock()
    mock_thread.id = "thread_456"
    mock_openai.beta.threads.create.return_value = mock_thread

    state = make_state()
    result = thread_manager_node(state)

    assert result.private.assistant_id == "asst_123"
    assert result.private.thread_id == "thread_456"
    mock_create_assistant.assert_called_once()
    mock_openai.beta.threads.create.assert_called_once()

@patch("code_agent.graph.execution.nodes.thread_manager.create_openai_assistant")
@patch("code_agent.graph.execution.nodes.thread_manager.openai")
def test_only_thread_id_missing(mock_openai, mock_create_assistant):
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    # assistant_id는 있고 thread_id만 없는 경우
    mock_thread = MagicMock()
    mock_thread.id = "thread_789"
    mock_openai.beta.threads.create.return_value = mock_thread

    state = make_state(assistant_id="asst_abc")
    result = thread_manager_node(state)

    # create_openai_assistant가 호출되지 않았는지 먼저 확인
    mock_create_assistant.assert_not_called()
    assert result.private.assistant_id == "asst_abc"
    assert result.private.thread_id == "thread_789"

@patch("code_agent.graph.execution.nodes.thread_manager.create_openai_assistant")
@patch("code_agent.graph.execution.nodes.thread_manager.openai")
def test_thread_id_already_exists(mock_openai, mock_create_assistant):
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    # thread_id가 이미 있으면 아무것도 생성하지 않음
    state = make_state(assistant_id="asst_exist", thread_id="thread_exist")
    result = thread_manager_node(state)

    assert result.private.assistant_id == "asst_exist"
    assert result.private.thread_id == "thread_exist"
    mock_create_assistant.assert_not_called()
    mock_openai.beta.threads.create.assert_not_called()


def test_create_openai_assistant_real():
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    load_dotenv()
    instructions = "테스트 assistant입니다."
    tools = [{"type": "code_interpreter"}]
    model = "gpt-4o"

    # 실제 assistant 생성 (create_openai_assistant 사용)
    assistant_id = create_openai_assistant(instructions, tools, model)
    assert assistant_id is not None

    # 실제 assistant 객체를 조회하여 instructions 확인
    assistant = openai.beta.assistants.retrieve(assistant_id)
    assert assistant.instructions == instructions

    # 생성된 assistant를 삭제 (cleanup)
    openai.beta.assistants.delete(assistant_id)

@patch("code_agent.graph.execution.nodes.thread_manager.openai")
def test_reuse_within_lifetime(mock_openai, monkeypatch):
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    # 최초 생성
    state = make_state()
    # node_options에 max_minutes만 덮어쓰기
    if state.node_options is None:
        state.node_options = {}
    if "thread_manager_node" not in state.node_options:
        state.node_options["thread_manager_node"] = {}
    state.node_options["thread_manager_node"]["max_minutes"] = 1
    # patch time.time to a fixed value
    monkeypatch.setattr("src.code_agent.graph.execution.nodes.thread_manager.time", time)
    result1 = thread_manager_node(state)
    asst_id_1 = result1.private.assistant_id
    thread_id_1 = result1.private.thread_id

    # 두 번째 호출: 1분 이내면 같은 id 재사용
    result2 = thread_manager_node(state)
    assert result2.private.assistant_id == asst_id_1
    assert result2.private.thread_id == thread_id_1

@patch("code_agent.graph.execution.nodes.thread_manager.create_openai_assistant")
@patch("code_agent.graph.execution.nodes.thread_manager.openai")
def test_expire_and_renew(mock_openai, mock_create_asst):
    thread_manager.ASSISTANT_THREAD_MAP.clear()
    mock_create_asst.side_effect = ["asst_1", "asst_new"]
    mock_thread1 = MagicMock()
    mock_thread1.id = "thread_1"
    mock_thread2 = MagicMock()
    mock_thread2.id = "thread_new"
    mock_openai.beta.threads.create.side_effect = [mock_thread1, mock_thread2]

    state = make_state()
    # node_options에 max_minutes만 덮어쓰기
    if state.node_options is None:
        state.node_options = {}
    if "thread_manager_node" not in state.node_options:
        state.node_options["thread_manager_node"] = {}
    state.node_options["thread_manager_node"]["max_minutes"] = (0.5/60)  # 0.5초로 만료 테스트
    result1 = thread_manager_node(state)
    asst_id_1 = result1.private.assistant_id
    thread_id_1 = result1.private.thread_id

    # 실제로 1초 대기
    time.sleep(1)

    # 두 번째 호출: 만료되어 새로운 id 생성
    state2 = make_state()
    if state2.node_options is None:
        state2.node_options = {}
    if "thread_manager_node" not in state2.node_options:
        state2.node_options["thread_manager_node"] = {}
    state2.node_options["thread_manager_node"]["max_minutes"] = (0.5/60)
    result2 = thread_manager_node(state2)
    assert result2.private.assistant_id == "asst_new"
    assert result2.private.thread_id == "thread_new"
    assert (asst_id_1, thread_id_1) != ("asst_new", "thread_new") 