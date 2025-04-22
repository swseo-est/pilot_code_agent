import openai
import asyncio
from code_agent.graph.state import CodeExecutionState
from code_agent.graph.execution.nodes.stream_callback import StreamBlockAssembler
import types


async def run_assistant_node(state: CodeExecutionState) -> CodeExecutionState:
    # node_options에서 옵션 우선 적용
    opts = (getattr(state, "node_options", None) or {}).get("run_assistant_node", {})
    timeout_sec = opts.get("timeout_sec", 60)
    use_callback = opts.get("use_callback", True)
    # stream_output_callback 등 다른 옵션도 필요시 여기에 추가

    if not (state.private.assistant_id and state.private.thread_id and state.private.message_id):
        raise ValueError("assistant_id, thread_id, message_id가 모두 필요합니다.")

    client = openai.OpenAI()
    response_format = get_response_format_schema()

    if use_callback:
        stream_output_callback = StreamBlockAssembler()
    else:
        stream_output_callback = None

    try:
        # stream=True로 실행
        with client.beta.threads.runs.create(
            thread_id=state.private.thread_id,
            assistant_id=state.private.assistant_id,
            response_format=response_format,
            stream=True
        ) as stream:
            last_run = None
            for event in stream:
                if stream_output_callback:
                    stream_output_callback(event)
                # run 상태 추적
                if hasattr(event, 'data') and getattr(event.data, 'object', None) == 'thread.run':
                    last_run = event.data
            if last_run:
                state.private.run_id = last_run.id
                state.private.run_status = last_run.status
                if last_run.status != "completed":
                    state.private.error_msg = f"Run이 정상적으로 완료되지 않았습니다. (status: {last_run.status})"
    except asyncio.TimeoutError:
        # 타임아웃 발생 시 run 취소 요청
        state.private.run_status = "timeout"
        try:
            if getattr(state.private, "thread_id", None) and getattr(state.private, "run_id", None):
                client.beta.threads.runs.cancel(
                    thread_id=state.private.thread_id,
                    run_id=state.private.run_id
                )
                state.private.error_msg = f"코드 실행시간이 {timeout_sec}초 를 초과하여 실행을 취소했습니다."
            else:
                state.private.error_msg = f"코드 실행시간이 {timeout_sec}초 를 초과했습니다. (run_id 또는 thread_id 없음)"
        except Exception as e:
            state.private.error_msg = f"코드 실행시간이 {timeout_sec}초 를 초과했고, 취소 요청 중 오류 발생: {e}"
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
