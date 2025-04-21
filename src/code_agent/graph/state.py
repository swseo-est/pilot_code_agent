from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class UserInputState(BaseModel):
    input: str = Field(..., description="자연어 프롬프트 (필수)")
    user_id: str = Field(..., description="사용자 고유 식별자 (필수, 클라이언트 제공)")
    session_id: str = Field(..., description="세션/스레드 식별자 (필수, 클라이언트 제공)")
    attachments: Optional[List[Any]] = Field(default_factory=list, description="첨부파일 리스트 (선택, 확장 가능)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="기타 메타데이터 (선택, 확장 가능)")

class CodeExecutionPrivateState(BaseModel):
    # --- OpenAI API 관련 식별자 ---
    assistant_id: Optional[str] = Field(default=None, description="OpenAI Assistant ID")
    thread_id: Optional[str] = Field(default=None, description="OpenAI Thread ID")
    message_id: Optional[str] = Field(default=None, description="OpenAI Message ID")
    run_id: Optional[str] = Field(default=None, description="OpenAI Run ID")

    # --- 실행 상태 및 에러 정보 ---
    run_status: Optional[str] = Field(default=None, description="Run의 상태 (completed, failed 등)")
    error_msg: Optional[Any] = Field(default=None, description="실행 중 발생한 에러 정보")
    handled_error: Optional[bool] = Field(default=None, description="에러가 핸들링되었는지 여부")

    # --- 메시지/실행 결과 객체 ---
    last_message: Optional[Any] = Field(default=None, description="마지막 메시지 객체 (추출 결과)")

    # --- structured output 관련 정보 ---
    executed: Optional[bool] = Field(default=None, description="실제 코드 실행 여부 (assistant의 executed 필드)")
    executed_code: Optional[Any] = Field(default=None, description="실행된 코드 블록 또는 JSON 파싱 결과")
    explanation: Optional[Any] = Field(default=None, description="코드/결과에 대한 설명 (structured output)")
    execution_result: Optional[Any] = Field(default=None, description="실행 결과 값 (structured output)")

class CodeExecutionState(BaseModel):
    user_input: UserInputState = Field(..., description="외부 입력 상태")
    private: CodeExecutionPrivateState = Field(default_factory=CodeExecutionPrivateState, description="코드 실행용 내부 상태")
    node_options: Optional[dict] = Field(default=None, description="그래프 실행 시 노드별 옵션 전달용") 