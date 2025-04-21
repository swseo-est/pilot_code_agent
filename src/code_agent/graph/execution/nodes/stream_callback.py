import json
from IPython.display import display, Markdown

class StreamBlockAssembler:
    def __init__(self):
        self.code_buffer = ""
        self.json_buffer = []
        self.code_started = False

    def print_code_lines(self, code: str):
        """코드 문자열을 줄 단위로 출력, [코드] 헤더는 한 번만 출력"""
        if not self.code_started:
            print("\n[코드]\n")
            self.code_started = True
        for line in code.splitlines():
            print(line)

    def __call__(self, event):
        # 코드 생성 delta (실시간)
        if getattr(event, "event", None) == "thread.run.step.delta":
            tool_calls = getattr(event.data.delta.step_details, "tool_calls", [])
            for block in tool_calls:
                if getattr(block, "code_interpreter", None) and getattr(block.code_interpreter, "input", None):
                    self.code_buffer += block.code_interpreter.input
                    while '\n' in self.code_buffer:
                        line, self.code_buffer = self.code_buffer.split('\n', 1)
                        self.print_code_lines(line)
        # 메시지(설명/결과/실행여부) 생성 delta (최종)
        elif getattr(event, "event", None) == "thread.message.delta":
            content_blocks = getattr(event.data.delta, "content", [])
            for block in content_blocks:
                text = getattr(block.text, "value", "")
                self.json_buffer.append(text)
                try:
                    json_str = "".join(self.json_buffer)
                    if json_str.startswith("{") and json_str.endswith("}"):
                        data = json.loads(json_str)
                        # 코드가 실시간으로 출력되지 않았다면, 여기서 줄 단위로 출력
                        if not self.code_started and data.get("code"):
                            self.print_code_lines(data["code"])
                        print("\n[설명]")
                        print(data.get('explanation', ''))
                        print("\n[실행 결과]")
                        print(data.get('result', ''))
                        print("\n[실행 여부]:", data.get('executed', ''))
                        self.json_buffer.clear()
                except Exception:
                    pass 