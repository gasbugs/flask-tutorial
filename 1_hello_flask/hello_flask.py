"""
Flask 입문 예제 — 가장 간단한 웹 서버 만들기

Flask는 Python으로 웹 서버를 만들 수 있는 가벼운 프레임워크입니다.
이 파일을 실행하면 브라우저에서 'Hello Flask!'를 볼 수 있습니다.
"""
from flask import Flask  # Flask 클래스를 가져옵니다. 웹 서버 역할을 합니다.

# Flask 앱 객체를 만듭니다. __name__은 현재 파일 이름을 의미합니다.
app = Flask(__name__)


# @app.route('/')는 "브라우저에서 '/' 주소로 접속하면 이 함수를 실행해라"는 뜻입니다.
@app.route('/')
def index():
    """브라우저에서 루트 주소('/')에 접속하면 'Hello Flask!' 문자열을 응답합니다."""
    return 'Hello Flask!'


# 이 파일을 직접 실행할 때만 웹 서버를 시작합니다.
# host='0.0.0.0'은 같은 네트워크의 다른 기기에서도 접속 가능하게 합니다.
# port=80은 기본 웹 포트(주소창에 포트 번호 없이 접속 가능)입니다.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
