import os
import sys
from dotenv import load_dotenv
from google import genai

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

def chat_with_llm(chat_session, user_message: str) -> str:
    response = chat_session.send_message(user_message)
    return response.text

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("오류: GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    client = genai.Client(api_key=api_key)
    chat_session = client.chats.create(model="gemini-2.5-flash-lite")

    print("Google AI Studio 챗봇 시작 (종료: 'exit')")
    print("-" * 40)

    while True:
        user_input = input("나: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("종료합니다.")
            break

        response = chat_with_llm(chat_session, user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    main()

