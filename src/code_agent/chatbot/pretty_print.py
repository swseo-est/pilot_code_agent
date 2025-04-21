from IPython.display import display, Markdown

def pretty_print_result(result):
    private = result["private"] if isinstance(result, dict) else getattr(result, "private", None)
    code = getattr(private, "executed_code", None)
    explanation = getattr(private, "explanation", None)
    exec_result = getattr(private, "execution_result", None)
    executed = getattr(private, "executed", None)
    run_status = getattr(private, "run_status", None)
    error_msg = getattr(private, "error_msg", None)

    # 에러 상태 우선 출력
    if run_status in {"failed", "timeout", "parsing_failed", "no_message"}:
        display(Markdown(f"**[{run_status}]**: {error_msg }"))
        return

    # if code:
    #     display(Markdown(f"**[코드]**\n```python\n{code}\n```"))
    # if explanation:
    #     display(Markdown(f"**[설명]**\n{explanation}"))
    # if exec_result:
    #     display(Markdown(f"**[실행 결과]**\n```\n{exec_result}\n```"))
    # if executed is not None:
    #     display(Markdown(f"**[실행 여부]**: {executed}"))
 