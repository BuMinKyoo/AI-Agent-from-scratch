import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

def add_numbers(a: float, b: float) -> float:
    """두 숫자를 더해서 합을 반환합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자

    Returns:
        a와 b의 합
    """
    print(f"[도구 호출됨] add_numbers(a={a}, b={b})")
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """두 숫자를 곱해서 곱을 반환합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자

    Returns:
        a와 b의 곱
    """
    print(f"[도구 호출됨] multiply_numbers(a={a}, b={b})")
    return a * b

MAX_RETRIES = 3
RETRY_DELAY_SEC = 2

TOOLS = {
    "add_numbers": add_numbers,
    "multiply_numbers": multiply_numbers,
}

def send_with_retry(chat_session, message):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return chat_session.send_message(message)
        except errors.ServerError as e:
            if attempt < MAX_RETRIES:
                print(f"[재시도 {attempt}/{MAX_RETRIES - 1}] 서버 오류({e.code}) — {RETRY_DELAY_SEC}초 후 다시 시도합니다.")
                time.sleep(RETRY_DELAY_SEC)
            else:
                raise

def extract_function_calls(response):
    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        return []
    return [part.function_call for part in candidate.content.parts if part.function_call]

def chat_with_llm(chat_session, user_message: str) -> str:
    response = send_with_retry(chat_session, user_message)

    while True:
        function_calls = extract_function_calls(response)
        if not function_calls:
            return response.text

        if len(function_calls) > 1:
            print(f"[병렬 호출 감지] {len(function_calls)}개의 도구를 동시에 실행합니다.")

        response_parts = []
        for fc in function_calls:
            fn_name = fc.name
            fn_args = dict(fc.args)
            print(f"[모델이 도구 호출 요청] {fn_name}({fn_args})")

            if fn_name in TOOLS:
                result = TOOLS[fn_name](**fn_args)
                response_payload = {"result": result}
            else:
                response_payload = {"error": f"알 수 없는 함수: {fn_name}"}

            print(f"[도구 결과를 모델에 재전달] {fn_name} → {response_payload}")

            response_parts.append(types.Part.from_function_response(
                name=fn_name,
                response=response_payload,
            ))

        response = send_with_retry(chat_session, response_parts)

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("오류: GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    client = genai.Client(api_key=api_key)
    chat_session = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            tools=[add_numbers, multiply_numbers],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )

    print("Google AI Studio 챗봇 시작 (종료: 'exit')")
    print("-" * 40)

    while True:
        user_input = input("나: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("종료합니다.")
            break

        try:
            response = chat_with_llm(chat_session, user_input)
            print(f"AI: {response}")
        except errors.ServerError as e:
            print(f"[오류] 서버가 계속 응답하지 않습니다 ({e.code}). 잠시 후 다시 시도해주세요.")
        except errors.APIError as e:
            print(f"[오류] API 호출 실패: {e}")

if __name__ == "__main__":
    main()

