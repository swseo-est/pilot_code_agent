from langgraph.graph import StateGraph, START, END
from code_agent.graph.state import CodeExecutionState
from code_agent.graph.execution.nodes.thread_manager import thread_manager_node
from code_agent.graph.execution.nodes.message_append import message_append_node
from code_agent.graph.execution.nodes.run_assistant import run_assistant_node
from code_agent.graph.execution.nodes.extract_result import extract_result_node
from code_agent.graph.execution.nodes.error_handler import error_handler_node
# (추후) render_output_node import 필요

def build_execution_subgraph() -> StateGraph:
    """
    코드 실행 서브그래프를 빌드하여 반환합니다.
    (START → thread_manager_node → message_append_node → run_assistant_node → extract_result_node or error_handler_node → END)
    :return: StateGraph (LangGraph)
    """
    
    graph = StateGraph(CodeExecutionState)
    graph.add_node("thread_manager_node", thread_manager_node)
    graph.add_node("message_append_node", message_append_node)
    graph.add_node("run_assistant_node", run_assistant_node)
    graph.add_node("extract_result_node", extract_result_node)
    graph.add_node("error_handler_node", error_handler_node)
    graph.add_edge(START, "thread_manager_node")
    graph.add_edge("thread_manager_node", "message_append_node")
    graph.add_edge("message_append_node", "run_assistant_node")
    # 조건부 분기: run_status가 completed면 extract_result_node, 아니면 error_handler_node
    def run_status_router(state):
        return "extract_result_node" if state.private.run_status == "completed" else "error_handler_node"
    graph.add_conditional_edges(
        "run_assistant_node",
        run_status_router,
        ["extract_result_node", "error_handler_node"],
    )
    graph.add_edge("extract_result_node", "error_handler_node")
    graph.add_edge("error_handler_node", END)
    return graph


import asyncio

async def main(input_json_path):
    from code_agent.data.data_loader import load_json_as_dict
    from code_agent.graph.execution.nodes.entry_node import entry_node

    # JSON 로드 및 input 추출
    user_input_dict = load_json_as_dict(input_json_path)
    print("[TEST] Loaded user input:", user_input_dict)

    # entry_node에 전달하여 CodeExecutionState 생성
    code_exec_state = entry_node(user_input_dict)

    # 그래프 구조 출력
    graph = build_execution_subgraph()
    print("[TEST] Nodes:", list(graph.nodes))
    print("[TEST] Edges:")
    for src, dst in graph.edges:
        print(f"  {src} -> {dst}")

    # 그래프 빌드 및 컴파일 후 실행 테스트 (async)
    compiled_graph = graph.compile()
    result = await compiled_graph.ainvoke(code_exec_state)
    print("[TEST] Graph execution result:", result)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(main("user_input_examples/simple_example.json"))
    asyncio.run(main("user_input_examples/syntax_error_example.json"))
