import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
from flask import Flask, request, jsonify

# .env 파일에서 환경 변수 불러오기
load_dotenv(dotenv_path='fire.env')

# 환경 변수에서 API 키 가져오기
api_key = os.environ.get("GEMINI_API_KEY")

# API 키 환경변수 오류 발생 시
if not api_key:
    print("오류: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    exit()

# Gemini API에 API 키 설정
genai.configure(api_key=api_key)

# Gemini 모델 'gemini-2.5-flash' 사용
model = genai.GenerativeModel('gemini-2.5-flash')

# 전세 체크리스트
JEONSE_CHECKLIST = """
[전세 계약 전 필수 확인 체크리스트] 📝 

안전한 계약을 위해 아래 사항들을 반드시 확인하고 진행하세요!

## 1. 서류 확인 (가장 중요!)
- **등기부등본** : 계약하려는 집의 신분증입니다. (전입세대 열람 전 확인 필수!!) 
  '갑구'에서 실제 소유주가 누구인지, '을구'에서 근저당권(빚), 가압류 등 위험 요소가 있는지 꼭 확인하세요.
- **건축물대장** : 건물의 실제 용도와 일치 여부를 확인합니다. 
  불법 건축물은 아닌지, 계약하려는 호수의 용도가 '주거용'으로 되어 있는지 확인하세요. 
  (근린생활시설을 불법 개조한 경우 보증보험 가입이 거절될 수 있습니다.)
- **집주인 신분증** : 등기부등본 상의 소유주와 계약 당사자가 동일인물인지 신분증으로 대조 확인해야 합니다.

## 2. 권리 관계 확인
- **선순위 권리 확인** : 나보다 먼저 돈을 받을 권리(근저당 등)가 있는지, 
  있다면 그 금액이 집값에 비해 너무 높지 않은지 확인해야 합니다. 
  (집값의 70%를 넘으면 위험 신호!)
- **대리인 계약 시** : 집주인이 아닌 대리인과 계약 시, 
  집주인의 인감증명서가 첨부된 위임장을 반드시 '원본'으로 받아야 합니다. 
  (영상 통화로 집주인 본인 의사 확인 추천)

## 3. 보증금 보호
- **전세보증금 반환 보험 가입 가능 여부**: 계약 전에 해당 주택이 
  HUG 주택도시보증공사나 SGI서울보증보험의 보증보험에 가입 가능한 매물인지 미리 확인해보는 것이 가장 안전합니다.

궁금한 서류 이름이나 확인 방법에 대해 질문해주시면 더 자세히 알려드릴게요!
"""

# Gemini API 호출 함수
def chat_with_gemini(user_input):
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"오류: API 호출 중 문제가 발생했습니다. ({e})"

# Flask 앱 생성
app = Flask(__name__)

# 로그 파일 경로
log_file_path = "chat_log.txt"

# 라우트 설정
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # 로그 파일 열기 (텍스트 추가 모드)
    with open(log_file_path, 'a', encoding='utf-8') as f:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n{'='*50}\n")
        f.write(f"새로운 대화 요청 : {current_time}\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"나 : {user_message}\n")

        # 특정 키워드 트리거 체크
        trigger_keywords = ["체크리스트", "확인할 사항", "확인 사항", "계약 전", "조심", "주의", "예방"]
        if '전세' in user_message and any(keyword in user_message for keyword in trigger_keywords):
            response_text = JEONSE_CHECKLIST
        else:
            response_text = chat_with_gemini(user_message)

        # 로그 파일에 챗봇 답변 기록
        f.write(f"챗봇 : {response_text}\n\n")

    return jsonify({"response": response_text})


if __name__ == "__main__":
    print("안녕하세요! LAWKICK 법률 상담 챗봇 서버가 시작되었습니다.")
    app.run(debug=True)
