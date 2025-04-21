from code_agent.graph.execution.build import build_execution_subgraph

def build_and_compile_graph():
    graph = build_execution_subgraph()
    return graph.compile() 