from code_agent.data.data_loader import load_json_as_dict
from code_agent.graph.supervisor import supervisor_node, router_edge
from code_agent.graph.execution.nodes.entry_node import entry_node
from langgraph.graph import StateGraph

# 1. State 정의 (dict 기반)
class SimpleState(dict):
    pass

# 2. LangGraph 그래프 생성
graph = StateGraph(SimpleState)

# 3. 노드 등록
graph.add_node("supervisor_node", supervisor_node)
graph.add_node("entry_node", entry_node)
# (추후) graph.add_node("fallback_node", fallback_node)

# 4. 조건부 분기(conditional edge) 정의
graph.add_conditional_edges(
    "supervisor_node",
    router_edge,
    {
        "code": "entry_node",
        "fallback": "entry_node"  # fallback_node 미구현 시 임시로 entry_node로 연결
    }
)

graph.set_entry_point("supervisor_node")
graph.set_finish_point("entry_node")

# 5. 그래프 빌드
built_graph = graph.compile()

def main():
    # 입력 데이터 로드
    user_input = load_json_as_dict("user_input_examples/simple_example.json")
    print("[User Input]", user_input)

    # LangGraph 실행
    result = built_graph.invoke(user_input)
    print("[LangGraph Result]", result)

    # (추후) entry_node, thread_manager_node 등 단계별로 추가 예정

if __name__ == "__main__":
    main() 