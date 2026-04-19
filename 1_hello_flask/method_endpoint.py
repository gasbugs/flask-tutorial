"""
HTTP 메서드와 엔드포인트 이름 지정 예제

HTTP 메서드란 브라우저나 앱이 서버에 요청하는 '방식'입니다.
- GET: 데이터를 조회할 때 (브라우저 주소창 입력이 대표적인 GET 요청)
- POST: 데이터를 전송할 때 (회원가입, 글쓰기 등)

엔드포인트(endpoint)란 URL에 연결된 함수를 부르는 이름입니다.
기본값은 함수 이름이지만, endpoint= 로 직접 지정할 수 있습니다.
"""
from flask import Flask  # 웹 서버를 만들기 위한 Flask 가져오기

app = Flask(__name__)


# methods=["GET"]: GET 요청만 허용합니다.
# endpoint="hello-endpoint": 이 라우트의 이름을 "hello-endpoint"로 지정합니다.
#   url_for("hello-endpoint")처럼 이름으로 URL을 참조할 때 사용합니다.
@app.route("/hello", methods=["GET"], endpoint="hello-endpoint")
def hello():
    """/hello 주소로 GET 요청이 오면 'Hello, Flask!'를 응답합니다."""
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run()
