import openai
from code_agent.graph.state import CodeExecutionState
import time

# 인메모리 매핑 저장소
# key: (user_id, session_id), value: (assistant_id, thread_id, created_at)
ASSISTANT_THREAD_MAP = {}

def create_openai_assistant(instructions: str, tools: list, model: str) -> str:
    """
    OpenAI Assistant를 생성하고, assistant_id를 반환합니다.
    :param instructions: 어시스턴트의 역할/지침
    :param tools: 사용할 툴 목록 (예: [{"type": "code_interpreter"}])
    :param model: 사용할 LLM 모델명 (예: "gpt-4o")
    :return: 생성된 assistant의 id (str)
    """
    assistant = openai.beta.assistants.create(
        instructions=instructions,
        tools=tools,
        model=model
    )
    return assistant.id

def thread_manager_node(state: CodeExecutionState) -> CodeExecutionState:
    """
    사용자별 assistant_id 및 thread_id를 관리합니다. (OpenAI API 연동)
    - assistant_id: 없으면 동적으로 생성
    - thread_id: state에 없으면 openai API로 생성
    - user_id, session_id를 이용해 인메모리 매핑 저장소에서 재사용
    - 최대 max_minutes(기본 60.0분, float)까지 유지, 초과 시 새로 생성
    """
    opts = (getattr(state, "node_options", None) or {}).get("thread_manager_node", {})
    max_minutes = opts.get("max_minutes", 60.0)
    instructions = opts.get("instructions", None)
    tools = [{"type": "code_interpreter"}]
    model = opts.get("model", "gpt-4o")

    assert instructions, "instructions is required"

    key = (state.user_input.user_id, state.user_input.session_id)
    now = time.time()
    # 1. 이미 매핑이 있고, 만료되지 않았으면 재사용
    if key in ASSISTANT_THREAD_MAP:
        assistant_id, thread_id, created_at = ASSISTANT_THREAD_MAP[key]
        if now - created_at < max_minutes * 60:
            state.private.assistant_id = assistant_id
            state.private.thread_id = thread_id
            return state
        # 만료된 경우: 기존 것을 폐기(필요시 openai에서 삭제), 새로 생성

    # 2. 없거나 만료된 경우 새로 생성
    if not state.private.assistant_id:
        state.private.assistant_id = create_openai_assistant(instructions, tools, model)

    if not state.private.thread_id:
        thread = openai.beta.threads.create()
        state.private.thread_id = thread.id

    # 3. 매핑 저장 (생성 시각 포함)
    ASSISTANT_THREAD_MAP[key] = (state.private.assistant_id, state.private.thread_id, now)
    return state
