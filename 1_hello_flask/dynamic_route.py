"""
동적 라우팅(Dynamic Route) 예제

'동적 라우팅'이란 URL 주소의 일부가 변수처럼 바뀌는 경우를 말합니다.
예: /hello/철수, /hello/영희 처럼 이름에 따라 다른 응답을 줄 수 있습니다.
"""
from flask import Flask, url_for  # url_for: 함수 이름으로 URL을 자동 생성해주는 도구

app = Flask(__name__)


@app.route("/")
def hello():
    """루트 주소('/')에 접속하면 'Hello Page!'를 응답합니다."""
    return "Hello Page!"


# <username> 부분이 변수입니다. 접속하는 사람마다 다른 값이 들어옵니다.
# 예: /profile/alice → username = "alice"
@app.route('/profile/<username>/')
def get_profile(username):
    """URL에 포함된 사용자 이름을 꺼내서 응답합니다."""
    return 'profile : ' + username


# <string:name>은 "name이라는 이름의 문자열 변수"를 URL에서 받겠다는 뜻입니다.
# methods=["GET"]은 GET 방식의 요청만 허용합니다(브라우저 주소창 접속은 GET 방식).
@app.route("/hello/<string:name>", methods=["GET"])
def hello_name(name):
    """/hello/이름 형태로 접속하면 이름을 포함한 인사말을 응답합니다."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # url_for('get_profile', username='flask')는 '/profile/flask/' 라는 URL을 만들어줍니다.
    # 함수 이름이 바뀌어도 URL을 하드코딩하지 않아도 되어 유지보수가 편합니다.
    with app.test_request_context():
        print(url_for('get_profile', username='flask'))
    app.run()
