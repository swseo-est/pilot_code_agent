import ast
from datasets import load_dataset
from code_agent.chatbot.graph_utils import build_and_compile_graph
from code_agent.graph.execution.nodes.entry_node import entry_node


def run_tests_exec(generated_code, test_cases):
    passed = 0
    num_error = 0
    total = len(test_cases)
    global_env = {}

    try:
        exec(generated_code, global_env)  # 함수 정의 실행
    except Exception as e:
        print("[ERROR] 코드 실행 실패:", e)
        return 0, total, 3

    for i, test in enumerate(test_cases):
        try:
            exec(test, global_env)  # 같은 env에서 테스트 실행
            passed += 1
        except AssertionError:
            print(f"[FAIL] Test {i+1}: Assertion failed")
        except Exception as e:
            print(f"[ERROR] Test {i+1}: {e}")
            num_error += 1

    return passed, total, num_error



def extract_first_function_name(code: str) -> str:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None


async def create_source_code(task: str) -> str:
    user_input_dict = {
    "input": task,
    "user_id": "test_user",
    "session_id": "test_session",
    "attachments": [],
    "metadata": {}
    }
    compiled_graph = build_and_compile_graph()

    code_exec_state = entry_node(user_input_dict, config_path="config_mbpp_benchmark.yaml")
    result = await compiled_graph.ainvoke(code_exec_state)
    return result


def generate_mdpp_data():
    mbpp = load_dataset("mbpp")

    num_total = 0
    for key in mbpp.keys():
        num_task = len(mbpp[key])
        num_total += num_task
    print(num_total)

    for key in mbpp.keys():
        for s in mbpp[key]:
            task = s['text']
            code_ground_truth = s['code']
            test_list = s['test_list']

            yield (task, code_ground_truth, test_list)

