# Code Agent Chatbot 테스트 안내

이 프로젝트는 LangGraph 기반의 Python 코드 에이전트 챗봇 예제입니다.

## 1. 프로젝트 클론

```bash
# 저장소를 클론합니다.
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_NAME>
```

## 2. Python 환경 준비

** Python 버전: 3.13 **

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
```

## 3. 의존성 설치 (uv.lock 기반)

[uv](https://github.com/astral-sh/uv) 설치 후 아래 명령으로 완전 동일한 환경을 재현할 수 있습니다.

```bash
pip install uv  # 또는 pipx install uv
uv pip sync
```

### (requirements.txt/pyproject.toml을 수정한 경우)

의존성 파일을 수정했다면 아래 명령으로 uv.lock을 갱신한 뒤, 다시 설치하세요.

```bash
uv pip compile  # pyproject.toml 또는 requirements.txt가 있을 때
uv pip sync
```

## 4. 환경 변수 설정 (**필수**)

OpenAI API 키 등 환경변수가 반드시 필요합니다. 

아래 명령으로 예시 파일을 복사해 .env 파일을 만드세요:

```bash
cp env.example .env  # Windows: copy env.example .env
```

.env 파일을 열어 아래와 같이 환경변수를 입력하세요:

```
OPENAI_API_KEY=sk-...
```

## 5. Jupyter 노트북 실행

Jupyter가 없다면 설치:
```bash
uv pip install notebook
```

노트북 서버 실행:
```bash
jupyter notebook
```

## 6. 챗봇 테스트

Jupyter에서 `notebooks/run_chatbot.ipynb` 파일을 엽니다.

- 첫 번째 셀을 실행하면 챗봇 대화가 시작됩니다.
- 프롬프트에 질문을 입력하면 실시간으로 코드, 설명, 실행 결과가 출력됩니다.
- '종료' 또는 'exit'을 입력하면 대화가 종료됩니다.
