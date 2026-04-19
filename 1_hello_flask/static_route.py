"""
정적 라우팅(Static Route) 예제

'정적 라우팅'이란 URL 주소가 고정된 경우를 말합니다.
예: /hello 라는 주소는 항상 같은 페이지를 보여줍니다.
"""
from flask import Flask  # 웹 서버를 만들기 위한 Flask 가져오기

app = Flask(__name__)  # Flask 앱 객체 생성


# /hello 주소로 접속하면 이 함수가 실행됩니다.
# URL이 고정되어 있으므로 '정적 라우팅'이라고 부릅니다.
@app.route("/hello")
def hello():
    """'/hello' 주소에 접속하면 HTML 형식의 'Hello World!'를 응답합니다."""
    return "<h1>Hello World!</h1>"  # <h1>은 HTML에서 가장 큰 제목 태그입니다.


if __name__ == "__main__":
    # debug=True: 코드를 수정하면 서버가 자동으로 재시작됩니다. 개발할 때 편리합니다.
    app.run()
