import pytest
from code_agent.graph.execution.build import main as build_main
from code_agent.data.data_loader import load_json_as_dict
from dotenv import load_dotenv
load_dotenv()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_file",
    [
        "user_input_examples/simple_example.json",
        "user_input_examples/syntax_error_example.json",
    ]
)
async def test_build_main_with_loader(input_file):
    # data_loader를 이용해 입력 dict를 미리 확인(옵션)
    user_input = load_json_as_dict(input_file)
    print("[TEST] Loaded input:", user_input)
    # main 함수에 상대경로 그대로 전달 (main 내부에서 loader 사용)
    await build_main(input_file) 