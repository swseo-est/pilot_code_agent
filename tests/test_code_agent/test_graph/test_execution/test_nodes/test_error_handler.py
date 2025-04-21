import pytest
from code_agent.graph.execution.nodes.error_handler import error_handler_node
from code_agent.graph.state import CodeExecutionState, CodeExecutionPrivateState, UserInputState

def make_state(run_status="completed", error=None, execution_result=None):
    private = CodeExecutionPrivateState(
        run_status=run_status,
        error=error,
        execution_result=execution_result
    )
    return CodeExecutionState(
        user_input=UserInputState(input="test", user_id="u", session_id="s"),
        private=private
    )

def test_error_handler_run_status_not_completed():
    state = make_state(run_status="failed", execution_result="SyntaxError: ...")
    result = error_handler_node(state)
    # error_msg는 그대로 None이어야 함
    assert result.private.error_msg is None

def test_error_handler_error_field_present():
    state = make_state(error="Some error", execution_result="SyntaxError: ...")
    result = error_handler_node(state)
    assert result.private.error_msg == "SyntaxError: ..."

def test_error_handler_execution_result_with_error_keyword():
    state = make_state(execution_result="SyntaxError: invalid syntax")
    result = error_handler_node(state)
    assert result.private.error_msg == "SyntaxError: invalid syntax"

def test_error_handler_execution_result_without_error_keyword():
    state = make_state(execution_result="정상 결과입니다.")
    result = error_handler_node(state)
    assert result.private.error_msg is None 