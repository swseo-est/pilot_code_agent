from code_agent.graph.state import UserInputState, CodeExecutionPrivateState, CodeExecutionState
import yaml


def entry_node(state: dict, config_path: str = None) -> CodeExecutionState:
    """
    supervisor_node의 출력을 받아 CodeExecutionState(user_input, private)로 변환
    :param state: supervisor_node의 출력(dict 또는 UserInputState)
    :param config_path: config_node.yaml 파일 경로 (옵션)
    :return: CodeExecutionState
    """
    user_input = UserInputState(**state)
    private = CodeExecutionPrivateState(**state)  # 초기화, 필요시 state에서 값 추출 가능
    # config_node.yaml 경로 계산 (기본값: src/code_agent/config_node.yaml)
    node_options = DEFAULT_NODE_OPTIONS.copy()
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_options = yaml.safe_load(f) or {}
            # yaml에 있는 필드만 덮어씀 (merge)
            for k, v in yaml_options.items():
                if k in node_options and isinstance(node_options[k], dict) and isinstance(v, dict):
                    node_options[k] = {**node_options[k], **v}
                else:
                    node_options[k] = v
    return CodeExecutionState(user_input=user_input, private=private, node_options=node_options)


DEFAULT_NODE_OPTIONS = {
    "run_assistant_node": {
        "timeout_sec": 60,
        # "stream_output_callback": None,  # 필요시 콜백 함수 경로 등으로 지정
    },
    "thread_manager_node": {
        "instructions": (
            "- 사용자의 요청에 따라 코드를 생성하고, 실행이 필요한 경우 실제로 실행하세요.\n"
            "- explanation은 한글로 반환하세요.\n"
            "- 반드시 아래와 같은 JSON 문자열만을 반환하세요(코드 블록 없이, 추가 설명 없이):\n"
            "  {\n"
            "    \"executed\": true,   // 실제 코드 실행 시 true, 실행하지 않은 경우 false\n"
            "    \"code\": \"...\\n\",\n"
            "    \"explanation\": \"...\",\n"
            "    \"result\": \"...\"\n"
            "  }\n"
            "- 생성된 코드의 마지막 라인 끝에는 반드시 '# [END]'라는 주석을 추가하세요."
            "- code 필드는 항상 마지막 줄에 빈 줄(개행)로 끝나도록 하세요.\n"
            "- 실행이 필요 없는 경우(예: 단순 설명, 코드 예시만 제공 등)에는 executed를 false로, 실행한 경우에는 true로 설정하세요.\n"
            "- 코드의 마지막은 빈 줄로 끝나야 합니다."
            "- 예시:\n"
            "  {\n"
            "    \"executed\": true,\n"
            "    \"code\": \"import random\\n# 랜덤하게 1부터 100 사이의 정수를 생성합니다.\\nrandom_number = random.randint(1, 100)\\nrandom_number  # [END]\\n\\n\",\n"
            "    \"explanation\": \"random 모듈을 사용해 1~100 사이의 정수를 생성합니다.\",\n"
            "    \"result\": \"예: 42\"\n"
            "  }\n"
        ),
        "model": "gpt-4o",
        "max_minutes": 50.0,
    },
    # message_append_node, extract_result_node, error_handler_node 등은 옵션이 없거나 필요시 추가
}