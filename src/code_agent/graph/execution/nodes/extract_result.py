import openai
import asyncio
import json
from code_agent.graph.state import CodeExecutionState

async def extract_result_node(state: CodeExecutionState) -> CodeExecutionState:
    if not (state.private.thread_id and state.private.run_id):
        raise ValueError("thread_id, run_id가 모두 필요합니다.")

    client = openai.OpenAI()
    # 메시지 목록 조회 (최신순)
    messages = await asyncio.to_thread(
        client.beta.threads.messages.list,
        thread_id=state.private.thread_id
    )
    # run_id와 role이 assistant인 메시지 중 최신 메시지 추출
    assistant_messages = [
        m for m in messages.data
        if getattr(m, 'run_id', None) == state.private.run_id and getattr(m, 'role', None) == 'assistant'
    ]
    if assistant_messages:
        last_message = assistant_messages[0]
        state.private.last_message = last_message
        # 텍스트 추출 (OpenAI 메시지 구조에 따라 다름)
        if last_message.content and hasattr(last_message.content[0], 'text'):
            text_value = last_message.content[0].text.value
            try:
                parsed_json = json.loads(text_value)
                state.private.executed_code = parsed_json.get("code")
                state.private.explanation = parsed_json.get("explanation")
                state.private.execution_result = parsed_json.get("result")
                state.private.executed = parsed_json.get("executed")
            except Exception:
                state.private.run_status = "parsing_failed"
                state.private.executed_code = None
                state.private.explanation = None
                state.private.execution_result = None
                state.private.executed = None
                state.private.error_msg = "결과 파싱에 실패했습니다."

    else:
        state.private.last_message = None
        state.private.executed_code = None
        state.private.explanation = None
        state.private.execution_result = None
        state.private.executed = None
        state.private.run_status = "no_message"
        state.private.error_msg = "assistant 메시지가 반환되지 않았습니다."

    return state 