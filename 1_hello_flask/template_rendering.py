"""
Jinja2 템플릿 렌더링 예제

템플릿이란 HTML 파일에 Python 데이터를 끼워넣을 수 있는 틀입니다.
Flask는 Jinja2라는 템플릿 엔진을 내장하고 있습니다.
HTML 파일은 templates/ 폴더에 저장해야 Flask가 찾을 수 있습니다.
"""
from flask import Flask, render_template  # render_template: HTML 파일을 불러와 응답으로 만들어줍니다.

app = Flask(__name__)


# /name/이름 으로 접속하면 index.html 템플릿에 이름을 넣어서 응답합니다.
@app.route("/name/<string:name>")
def show_name(name):
    """URL에서 받은 이름을 templates/index.html 템플릿에 전달해 렌더링합니다."""
    # render_template("파일명", 변수명=값) 형태로 사용합니다.
    # 템플릿 파일 안에서 {{ name }} 으로 이 값을 출력할 수 있습니다.
    return render_template("index.html", name=name)


@app.route("/loop/<string:name>")
def show_loop(name):
    """이름과 영화 목록을 templates/loop.html 템플릿에 전달해 렌더링합니다."""
    # 딕셔너리 리스트 형태의 데이터를 템플릿에 넘길 수 있습니다.
    movies = [
        {'name': '타이타닉', 'year': 1998},
        {'name': '터미네이터', 'year': 1984}
    ]
    # 템플릿 안에서 {% for movie in movies %} 문법으로 반복 출력할 수 있습니다.
    return render_template("loop.html", name=name, movies=movies)


@app.route("/css")
def show_css():
    """CSS 스타일시트를 적용한 templates/css.html을 렌더링합니다."""
    return render_template("css.html")


if __name__ == "__main__":
    app.run()
