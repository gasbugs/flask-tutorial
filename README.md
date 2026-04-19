# Flask Tutorial

Flask 입문자를 위한 단계별 튜토리얼 프로젝트입니다.

---

## 환경 구성

### 1. Python 버전 확인

Python 3.9 이상이 필요합니다.

```bash
python3 --version
```

### 2. 가상환경(venv) 생성

가상환경은 프로젝트별로 패키지를 격리하여 관리하는 공간입니다.  
시스템 Python에 영향을 주지 않고 필요한 라이브러리만 설치할 수 있습니다.

```bash
# 프로젝트 루트에서 실행
python3 -m venv venv
```

### 3. 가상환경 활성화

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

활성화되면 프롬프트 앞에 `(venv)` 표시가 나타납니다.

```
(venv) $
```

### 4. 의존성 설치

```bash
pip install -r requirements.txt
```

### 5. 가상환경 비활성화

```bash
deactivate
```

---

## 예제 실행

### 1단계: 기본 Flask (`1_hello_flask/`)

Flask의 핵심 개념인 라우팅, 동적 URL, 템플릿 렌더링을 익힙니다.

```bash
# 최소 Flask 앱
python 1_hello_flask/hello_flask.py

# 동적 라우팅 (/hello/<name>, /profile/<username>)
python 1_hello_flask/dynamic_route.py

# HTTP 메서드 & 엔드포인트 이름 지정
python 1_hello_flask/method_endpoint.py

# Jinja2 템플릿 렌더링
python 1_hello_flask/template_rendering.py
```

브라우저에서 `http://127.0.0.1:5000` 으로 접속하여 확인합니다.

### 2단계: REST API (`2_cars_api/`)

`flask-restx`를 사용한 CRUD API와 Swagger UI 자동 문서화를 실습합니다.

```bash
cd 2_cars_api
python app.py
```

- API 서버: `http://127.0.0.1:5000`
- Swagger UI: `http://127.0.0.1:5000` (자동 생성)

**테스트 실행:**

```bash
cd 2_cars_api

# 전체 테스트
pytest

# 특정 테스트만 실행
pytest app_test.py::test_create_brand -v
```

### 3단계: Elasticsearch 연동 (`3_elasticsearch_with_python/`)

Elasticsearch에 데이터를 삽입하고 검색하는 방법을 익힙니다.

> **사전 요구사항:** Elasticsearch 8.x 서버가 `https://127.0.0.1:9200` 에서 실행 중이어야 합니다.  
> 기본 계정: `elastic` / `test1234`

```bash
cd 3_elasticsearch_with_python

# 순서대로 실행
python 1_connection.py      # 연결 확인
python 2_index_list.py      # 인덱스 목록 조회
python 3_data_insert.py     # 샘플 데이터 삽입
python 4_data_get.py        # 데이터 조회
python 5_data_search.py     # 검색 쿼리 실습
```

---

## 프로젝트 구조

```
flask-tutorial/
├── 1_hello_flask/          # Flask 기본 라우팅 예제
│   ├── hello_flask.py
│   ├── static_route.py
│   ├── dynamic_route.py
│   ├── method_endpoint.py
│   ├── template_rendering.py
│   ├── static/             # CSS 정적 파일
│   └── templates/          # Jinja2 HTML 템플릿
├── 2_cars_api/             # flask-restx REST API
│   ├── app.py              # API 서버 (자동차 CRUD)
│   ├── app_test.py         # pytest 테스트
│   └── sample_test.py      # pytest 기본 사용법 예제
├── 3_elasticsearch_with_python/   # Elasticsearch 연동
│   ├── 1_connection.py ~ 5_data_search.py
│   └── json/               # 샘플 데이터 (books, accounts 등)
├── requirements.txt        # 의존성 목록
└── README.md
```
