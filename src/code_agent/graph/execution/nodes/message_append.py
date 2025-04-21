import openai
from code_agent.graph.state import CodeExecutionState

def message_append_node(state: CodeExecutionState) -> CodeExecutionState:
    """
    OpenAI Thread에 사용자의 메시지를 추가하고, message_id를 state에 저장합니다.
    """
    if not (state.private.assistant_id and state.private.thread_id):
        raise ValueError("assistant_id와 thread_id가 모두 필요합니다.")

    message = openai.beta.threads.messages.create(
        thread_id=state.private.thread_id,
        role="user",
        content=state.user_input.input
    )
    state.private.message_id = message.id
    return state 