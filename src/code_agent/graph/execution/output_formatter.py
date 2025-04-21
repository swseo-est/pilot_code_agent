from code_agent.graph.state import CodeExecutionState
from typing import Any
from pydantic import BaseModel, Field

# OutputState 모델이 별도 파일에 있다면 import, 아니면 임시 정의
class OutputState(BaseModel):
    user_id: str = Field(..., description="사용자 고유 식별자")
    session_id: str = Field(..., description="세션/스레드 식별자")
    result: Any = Field(default=None, description="실행 결과 (텍스트, 파일, 이미지 등)")
    error: Any = Field(default=None, description="실행 중 발생한 에러 정보")
    metadata: dict = Field(default_factory=dict, description="추가 정보(확장 가능)")

def output_formatter_node(state: CodeExecutionState) -> OutputState:
    return OutputState(
        user_id=state.user_input.user_id,
        session_id=state.user_input.session_id,
        result=getattr(state.private, "final_output", None),
        error=state.private.error,
        metadata={
            "input": state.user_input.input,
            "executed_code": getattr(state.private, "executed_code", None),
            "explanation": getattr(state.private, "explanation", None),
            "run_status": getattr(state.private, "run_status", None),
            "handled_error": getattr(state.private, "handled_error", None),
            # 필요시 추가 필드
        }
    ) 