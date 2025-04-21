def supervisor_node(user_input: dict) -> dict:
    """
    입력받은 user_input에 대해 코드 실행 필요성(route)을 판단하여 반환합니다.
    현재는 항상 'code'로 반환하지만, 추후 LLM 또는 rule-based 분기 로직으로 확장 가능합니다.
    :param user_input: UserInputState dict
    :return: {'route': 'code'} 또는 {'route': 'fallback'}
    """
    # TODO: LLM 또는 rule-based 분기 로직으로 확장
    return {"route": "code"}


def router_edge(state: dict) -> str:
    """
    LangGraph 조건부 분기(conditional edge)에서 사용.
    state(dict)에서 'route' 값을 추출해 반환합니다.
    :param state: supervisor_node의 출력 dict
    :return: 'code' 또는 'fallback'
    """
    return state["route"] 