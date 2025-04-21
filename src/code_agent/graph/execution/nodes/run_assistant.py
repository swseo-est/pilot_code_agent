import openai
import asyncio
from code_agent.graph.state import CodeExecutionState


async def run_assistant_node(state: CodeExecutionState, timeout_sec: int = 60) -> CodeExecutionState:
    if not (state.private.assistant_id and state.private.thread_id and state.private.message_id):
        raise ValueError("assistant_id, thread_id, message_id가 모두 필요합니다.")

    client = openai.OpenAI()
    response_format = get_response_format_schema()
    try:
        run = await asyncio.wait_for(
            asyncio.to_thread(
                client.beta.threads.runs.create_and_poll,
                thread_id=state.private.thread_id,
                assistant_id=state.private.assistant_id,
                response_format=response_format
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


def get_response_format_schema():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "code_execution_result",
            "schema": {
                "type": "object",
                "properties": {
                    "executed": {
                        "type": "boolean",
                        "description": "실제 코드가 실행되었으면 true, 실행하지 않았으면 false"
                    },
                    "code": {
                        "type": "string",
                        "description": "생성된 파이썬 코드(실행된 코드 또는 예시 코드)"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "코드의 동작 원리, 목적, 결과에 대한 한글 설명"
                    },
                    "result": {
                        "type": "string",
                        "description": "코드 실행 결과(문자열로 변환된 값, 실행하지 않은 경우 일반 답변 문자열)"
                    }
                },
                "required": ["executed", "code", "explanation", "result"]
            }
        }
    }
