from code_agent.graph.state import CodeExecutionState

def error_handler_node(state: CodeExecutionState) -> CodeExecutionState:
    """
    실행 결과가 에러(실패, 예외, 비정상 등)인 경우 사용자에게 명확한 에러 메시지, 안내, 후처리 결과를 반환합니다.
    정상 결과라면 그대로 통과합니다.
    """
    error_keywords = ["Error", "Exception", "Traceback", "SyntaxError"]

    if state.private.run_status != "completed":
        return state
    if state.private.execution_result and isinstance(state.private.execution_result, str):
        if any(kw in state.private.execution_result for kw in error_keywords):
            # 실행 결과에 에러 키워드가 포함된 경우 error_msg에 저장
            state.private.error_msg = state.private.execution_result
    return state 