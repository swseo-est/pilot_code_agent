import openai
import asyncio
from code_agent.graph.state import CodeExecutionState


async def run_assistant_node(state: CodeExecutionState, timeout_sec: int = 60) -> CodeExecutionState:
    if not (state.private.assistant_id and state.private.thread_id and state.private.message_id):
        raise ValueError("assistant_id, thread_id, message_id가 모두 필요합니다.")

    client = openai.OpenAI()
    try:
        run = await asyncio.wait_for(
            asyncio.to_thread(
                client.beta.threads.runs.create_and_poll,
                thread_id=state.private.thread_id,
                assistant_id=state.private.assistant_id,
            ),
            timeout=timeout_sec
        )
        state.private.run_id = run.id
        state.private.run_status = run.status
        if run.status != "completed":
            state.private.error_msg = f"Run이 정상적으로 완료되지 않았습니다. (status: {run.status})"
    except asyncio.TimeoutError:
        state.private.run_status = "timeout"
        state.private.error_msg = f"Run timed out after {timeout_sec} seconds"
    return state