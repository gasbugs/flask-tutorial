# 설계 문서: K8s 스타일 Cars API 표준화 + OpenSearch 연동

**날짜:** 2026-04-19  
**수강 대상:** Python 기초 지식 보유, 웹/API 입문자

---

## 목표

1. `2_cars_api`를 Kubernetes REST API 스타일로 리팩터링
2. `4_opensearch_cars_api` 신규 구현 — K8s 스타일 + OpenSearch + 검색 + 프론트엔드

---

## K8s REST API 표준 (두 프로젝트 공통)

### URL 구조

```
GET    /api/v1/brands                        # 브랜드 목록
POST   /api/v1/brands                        # 브랜드 생성 (body에 이름)
GET    /api/v1/brands/{brand}                # 브랜드 조회
PUT    /api/v1/brands/{brand}                # 브랜드 수정 (2번: 실습과제, 4번: 구현)
DELETE /api/v1/brands/{brand}                # 브랜드 삭제

GET    /api/v1/brands/{brand}/models         # 모델 목록
POST   /api/v1/brands/{brand}/models         # 모델 생성
GET    /api/v1/brands/{brand}/models/{id}    # 모델 조회
PUT    /api/v1/brands/{brand}/models/{id}    # 모델 수정
DELETE /api/v1/brands/{brand}/models/{id}    # 모델 삭제

GET    /api/v1/cars/search?q=키워드          # 전체 텍스트 검색 (4번만)
```

### 응답 형식

**목록 응답:**
```json
{
  "apiVersion": "v1",
  "kind": "BrandList",
  "metadata": { "total": 2 },
  "items": [{ "name": "bentz" }, { "name": "bmw" }]
}
```

**단일 항목 응답:**
```json
{
  "apiVersion": "v1",
  "kind": "Brand",
  "metadata": { "name": "bentz" },
  "data": { ... }
}
```

**에러 응답:**
```json
{
  "apiVersion": "v1",
  "kind": "Status",
  "status": "Failure",
  "message": "Brand bentz not found",
  "code": 404
}
```

**HTTP 상태코드 기준:**

| 상황 | 코드 |
|------|------|
| 조회 성공 | 200 |
| 생성 성공 | 201 |
| 삭제 성공 | 204 |
| 잘못된 요청 | 400 |
| 리소스 없음 | 404 |
| 중복 | 409 |
| 미구현 | 501 |

---

## Sub-project 1: 2_cars_api 리팩터링

### 변경 범위

| 항목 | 현재 | 변경 후 |
|------|------|---------|
| URL prefix | `/cars/` | `/api/v1/brands` |
| 브랜드 생성 | `POST /cars/bentz` | `POST /api/v1/brands` + `{"name": "bentz"}` |
| 모델 생성 | `POST /cars/bentz/0` | `POST /api/v1/brands/bentz/models` + `{"model_id": 0, ...}` |
| 응답 형식 | `{"message": "ok", ...}` | K8s 표준 응답 |
| 에러 형식 | `{"message": "설명"}` | K8s Status 형식 |

### 변경하지 않는 것
- 메모리 딕셔너리 (`car_info`) 유지
- 페이지네이션 (`?page=1&size=10`) 유지 — metadata에 포함
- 입력 검증 유지
- 파일 구조 유지 (단일 `app.py`)

### 테스트
- 기존 테스트 URL/응답 형식 업데이트
- autouse fixture (`reset_car_info`) 유지

---

## Sub-project 2: 4_opensearch_cars_api 신규 구현

### 디렉터리 구조

```
4_opensearch_cars_api/
├── app.py                  # Flask 앱 진입점, Blueprint 등록
├── opensearch_client.py    # OpenSearch 연결 및 쿼리 담당
├── models.py               # flask-restx 스키마 + 인덱스 매핑 정의
├── routes/
│   ├── __init__.py
│   ├── brands.py           # /api/v1/brands 엔드포인트
│   ├── models.py           # /api/v1/brands/{brand}/models 엔드포인트
│   └── search.py           # /api/v1/cars/search 엔드포인트
├── templates/
│   ├── base.html           # 공통 레이아웃
│   ├── index.html          # 브랜드/모델 목록 페이지
│   └── search.html         # 검색 페이지
└── app_test.py             # pytest 테스트 (cars_test 인덱스 사용)
```

### 파일 역할

| 파일 | 역할 |
|------|------|
| `app.py` | Flask 앱 생성, Blueprint 등록, `/ui/` 경로 렌더링 |
| `opensearch_client.py` | OpenSearch 연결, CRUD/검색 쿼리 메서드 |
| `models.py` | flask-restx 스키마 + 인덱스 필드 매핑 |
| `routes/brands.py` | 브랜드 CRUD 라우트 (쿼리 로직은 client에 위임) |
| `routes/models.py` | 모델 CRUD 라우트 |
| `routes/search.py` | 검색 라우트 |
| `templates/` | Jinja2 템플릿 (서버 사이드 렌더링) |

### OpenSearch 데이터 구조

- **인덱스:** `cars` (운영), `cars_test` (테스트)
- **문서 ID:** `{brand}_{model_id}` (예: `bentz_0`)

**문서 형식:**
```json
{
  "brand": "bentz",
  "model_id": "0",
  "name": "e-class",
  "price": 1000000,
  "fuel_type": "gasoline",
  "fuel_efficiency": "9.1~13.2km/l",
  "engine_power": "367hp",
  "engine_cylinder": "I6"
}
```

### 검색 기능

`GET /api/v1/cars/search?q=e-class` — `multi_match` 쿼리로 전체 필드 검색:

```python
{
  "query": {
    "multi_match": {
      "query": "e-class",
      "fields": ["name", "brand", "fuel_type", "engine_cylinder"]
    }
  }
}
```

### 프론트엔드

**`GET /ui/`** — 메인 페이지
- 브랜드 목록 표시
- 브랜드 클릭 시 모델 목록 표시
- 브랜드/모델 추가·삭제 폼

**`GET /ui/search`** — 검색 페이지
- 검색어 입력 폼
- 결과를 테이블로 표시

**렌더링 방식:** Flask `render_template` + Jinja2 (서버 사이드), JS는 폼 제출 최소한만 사용

### 테스트 격리

```python
@pytest.fixture(autouse=True)
def setup_test_index():
    # 테스트 전: cars_test 인덱스 생성
    yield
    # 테스트 후: cars_test 인덱스 삭제
```

### OpenSearch 접속 정보

```python
hosts=[{"host": "127.0.0.1", "port": 9200}]
http_auth=("admin", "TeSt432!23$#")
use_ssl=True
verify_certs=False
```

---

## 구현 순서

1. Sub-project 1: 2_cars_api K8s 스타일 리팩터링
2. Sub-project 2: 4_opensearch_cars_api 신규 구현
