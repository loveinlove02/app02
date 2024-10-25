import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import base64
import json
import os

# Base64 인코딩된 Firebase 키를 읽어 디코딩
def load_firebase_credentials():
    base64_file_path = "firebase_key_base64.txt"

    with open(base64_file_path, "r") as f:
        encoded_data = f.read()

    decoded_data = base64.b64decode(encoded_data)
    json_data = json.loads(decoded_data)
    
    # 임시로 JSON 데이터를 사용하여 Credential 객체 생성
    return credentials.Certificate(json_data)

# Firebase 초기화 함수
def initialize_firebase():
    if not firebase_admin._apps:
        cred = load_firebase_credentials()
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://myapp-b3983-default-rtdb.firebaseio.com/'
        })

# Streamlit 앱 시작
st.title("Firebase Test App")

file_name = st.text_input("텍스트 파일의 이름을 입력하세요 (예: example.txt):")
name = st.text_input("이름을 입력하세요:")

# 초기화 버튼을 먼저 생성
if st.button("초기화"):
    initialize_firebase()
    st.success("Firebase가 초기화되었습니다!")

if file_name and name:
    file_path = os.path.join("question", file_name)  # question 폴더 안의 파일을 읽어옴

    try:
        # 파일을 열고 내용을 읽는 부분
        with open(file_path, "r", encoding="utf-8") as file:
            questions = []
            current_question = ""

            # 파일에서 각 줄을 읽어서 처리
            for line in file:
                line = line.rstrip()  # 줄 끝의 공백 제거
                if line == '-------------------------------------':
                    if current_question:
                        questions.append(current_question.strip())
                        current_question = ""
                else:
                    current_question += line + "\n"

            # 마지막 문제를 리스트에 추가
            if current_question:
                questions.append(current_question.strip())

            # answers 사전 생성
            answers = {}

            # 문제 출력 및 답변 입력 필드 생성
            for i, question in enumerate(questions, 1):
                st.code(question, language="python")  # 질문을 Python 코드 형식으로 출력
                answer = st.text_input(f"문제 {i}의 답을 입력하세요:", key=f"answer_{i}")
                answers[i] = answer

            submit_button = st.button("제출", type="primary")

            if submit_button:                    
                # 파이어베이스 DB에 데이터 저장
                ref = db.reference('exam')
                ref.child(name).set(answers)

                st.success(f"{name}님, 제출이 완료되었습니다!")

    except FileNotFoundError:
        st.error("해당 파일을 찾을 수 없습니다. 파일 이름을 확인해주세요.")
else:
    if not file_name:
        st.info("파일 이름을 입력하세요.")
    if not name:
        st.info("이름을 입력하세요.")
