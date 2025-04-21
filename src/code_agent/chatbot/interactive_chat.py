from code_agent.graph.execution.nodes.entry_node import entry_node
import asyncio

async def run_interactive_chat(compiled_graph, user_id, session_id, pretty_print_result, config_path=None):
    print("=== 챗봇 테스트 (종료하려면 '종료' 또는 'exit' 입력) ===")
    while True:
        input_text = input("\n[USER] ")
        if input_text.strip().lower() in ["종료", "exit"]:
            print("대화를 종료합니다.")
            break

        user_input_dict = {
            "input": input_text,
            "user_id": user_id,
            "session_id": session_id,
            "attachments": [],
            "metadata": {},
        }
        code_exec_state = entry_node(user_input_dict, config_path=config_path)
        result = await compiled_graph.ainvoke(code_exec_state)
        pretty_print_result(result) 