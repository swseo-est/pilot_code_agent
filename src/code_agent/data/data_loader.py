import os
import json

def get_data_abspath(relative_path: str) -> str:
    """
    주어진 data 폴더 기준 상대경로를 받아, 해당 파일의 절대경로를 반환합니다.
    :param relative_path: data 폴더 기준 상대경로 (예: 'benchmarks/example.json')
    :return: 절대경로 (str)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, relative_path)
    return os.path.abspath(abs_path)

def load_json_as_dict(relative_path: str) -> dict:
    """
    data 폴더 기준 상대경로의 JSON 파일을 읽어 dict로 반환합니다.
    :param relative_path: data 폴더 기준 상대경로 (예: 'benchmarks/example.json')
    :return: dict
    """
    abs_path = get_data_abspath(relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    data = load_json_as_dict("user_input_examples/simple_example.json")
    print("[TEST] Loaded data:", data) 