import pytest
from code_agent.graph.execution.nodes.entry_node import entry_node
from code_agent.graph.state import UserInputState, CodeExecutionPrivateState, CodeExecutionState

def test_entry_node_basic():
    # 입력 dict 준비
    input_dict = {
        "input": "파이썬으로 1+1을 계산해줘",
        "user_id": "user_001",
        "session_id": "sess_001",
        "attachments": [],
        "metadata": {"lang": "ko"}
    }
    # 함수 실행
    result = entry_node(input_dict)
    # 반환 타입 확인
    assert isinstance(result, CodeExecutionState)
    # user_input 필드 확인
    assert isinstance(result.user_input, UserInputState)
    assert result.user_input.input == "파이썬으로 1+1을 계산해줘"
    assert result.user_input.user_id == "user_001"
    assert result.user_input.session_id == "sess_001"
    assert result.user_input.attachments == []
    assert result.user_input.metadata == {"lang": "ko"}
    # private 필드 확인
    assert isinstance(result.private, CodeExecutionPrivateState)
    # private의 필드는 모두 None 또는 기본값이어야 함
    for field in result.private.__fields__:
        value = getattr(result.private, field)
        assert value is None or value == [] or value == {}

def test_entry_node_missing_optional_fields():
    # attachments, metadata 생략
    input_dict = {
        "input": "테스트",
        "user_id": "u",
        "session_id": "s"
    }
    result = entry_node(input_dict)
    assert result.user_input.attachments == []
    assert result.user_input.metadata == {}

def test_entry_node_invalid_input():
    # 필수 필드 누락 시 에러 발생
    with pytest.raises(Exception):
        entry_node({"user_id": "u", "session_id": "s"}) 