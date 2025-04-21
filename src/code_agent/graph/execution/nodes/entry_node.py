from code_agent.graph.state import UserInputState, CodeExecutionPrivateState, CodeExecutionState

def entry_node(state: dict) -> CodeExecutionState:
    """
    supervisor_node의 출력을 받아 CodeExecutionState(user_input, private)로 변환
    :param state: supervisor_node의 출력(dict 또는 UserInputState)
    :return: CodeExecutionState
    """
    user_input = UserInputState(**state)
    private = CodeExecutionPrivateState()  # 초기화, 필요시 state에서 값 추출 가능
    return CodeExecutionState(user_input=user_input, private=private) 