"""
POC: 코드 실행 에이전트 전체 흐름 (더미 함수 기반, 단일 스크립트)
- LangGraph 없이 함수 호출로 전체 분기/흐름을 시뮬레이션
- 실제 OpenAI 호출 없이 더미 데이터 반환
"""

def supervisor_node(state):
    # input에 '코드'라는 단어가 있으면 code route, 아니면 fallback
    if '코드' in state['input']:
        return {**state, 'route': 'code'}
    else:
        return {**state, 'route': 'fallback'}

def entry_node(state):
    # 내부 상태 초기화 (더미)
    return {**state, 'entry': True}

def thread_manager_node(state):
    # thread_id, assistant_id 할당 (더미)
    return {**state, 'thread_id': 'dummy_thread', 'assistant_id': 'dummy_assistant'}

def message_append_node(state):
    # 메시지 thread에 추가 (더미)
    return {**state, 'message_appended': True}

def run_assistant_node(state):
    # 코드 실행 (더미)
    # 에러 시 'error' 키 추가
    if state.get('simulate_error'):
        return {**state, 'error': '코드 실행 중 에러 발생'}
    return {**state, 'run_result': '3 * 4 * 5 = 60'}

def extract_result_node(state):
    # 실행 결과 추출 (더미)
    if 'error' in state:
        return state  # 에러는 그대로 전달
    return {**state, 'extracted_result': state.get('run_result', '결과 없음')}

def render_output_node(state):
    # 결과 시각화 (더미)
    if 'error' in state:
        return {**state, 'rendered_output': f"[에러] {state['error']}"}
    return {**state, 'rendered_output': f"[결과] {state['extracted_result']}"}

def error_handler_node(state):
    # 에러 메시지 출력 (더미)
    return {**state, 'handled_error': True, 'final_output': f"에러: {state.get('error', '알 수 없는 에러')}"}

def fallback_node(state):
    # 코드 실행이 필요 없는 경우 (더미)
    return {**state, 'final_output': '코드 실행이 필요하지 않습니다.'}

def output_formatter_node(state):
    # 외부에 반환할 output만 추출 (더미)
    return {'output': state.get('final_output', state.get('rendered_output', '출력 없음'))}

# --- POC 실행 흐름 ---
def poc_agent(user_input, simulate_error=False):
    state = {'input': user_input}
    if simulate_error:
        state['simulate_error'] = True
    # 1. supervisor_node
    state = supervisor_node(state)
    if state['route'] == 'code':
        # 2. 코드 실행 서브그래프
        state = entry_node(state)
        state = thread_manager_node(state)
        state = message_append_node(state)
        state = run_assistant_node(state)
        state = extract_result_node(state)
        if 'error' in state:
            state = error_handler_node(state)
        else:
            state = render_output_node(state)
            state['final_output'] = state['rendered_output']
    else:
        # 3. fallback
        state = fallback_node(state)
    # 4. output_formatter_node
    output = output_formatter_node(state)
    return output

if __name__ == "__main__":
    # 정상 실행 예시
    user_input = "세 수의 곱을 구하는 코드를 짜줘"
    print("[정상 실행]", poc_agent(user_input))

    # fallback 예시
    user_input2 = "오늘 날씨 어때?"
    print("[fallback 실행]", poc_agent(user_input2))

    # 에러 시뮬레이션 예시
    user_input3 = "코드 실행 중 에러를 시뮬레이션해줘"
    print("[에러 시뮬레이션]", poc_agent(user_input3, simulate_error=True)) 