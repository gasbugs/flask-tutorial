# OpenSearch Cars API 문서 (K8s 스타일)

OpenSearch를 백엔드로 사용하는 자동차 정보 REST API입니다. Kubernetes REST API 스타일을 따르며, 전체 텍스트 검색 기능을 제공합니다.

> **Swagger UI**: 서버 실행 후 `http://127.0.0.1:5001/docs` 접속

---

## 사전 준비

### OpenSearch 서버 실행

```bash
cd opensearch-docker-compose
podman-compose up -d   # 또는 docker compose up -d
```

서버 준비 확인:
```bash
curl -sk https://127.0.0.1:9200 -u admin:'TeSt432!23$#'
# {"name":"opensearch-node1", ...} 가 출력되면 준비 완료
```

### 앱 서버 실행

```bash
cd 4_opensearch_cars_api
python app.py
# http://127.0.0.1:5001 에서 실행됩니다.
```

---

## 프로젝트 구조

```
4_opensearch_cars_api/
├── app.py                  # Flask 앱 진입점, UI 라우트
├── opensearch_client.py    # OpenSearch CRUD + 검색 클라이언트
├── models.py               # flask-restx 스키마 + 인덱스 매핑
├── routes/
│   ├── __init__.py         # k8s_list / k8s_item / k8s_error 헬퍼
│   ├── brands.py           # 브랜드 CRUD 라우트
│   ├── models.py           # 모델 CRUD 라우트
│   └── search.py           # 검색 라우트
├── templates/
│   ├── base.html
│   ├── index.html          # 브랜드/모델 관리 UI
│   └── search.html         # 검색 UI
└── app_test.py
```

---

## OpenSearch 데이터 구조

- **인덱스**: `cars` (운영), `cars_test` (테스트)
- **브랜드 문서 ID**: `brand__{brand}` (예: `brand__bentz`)
- **모델 문서 ID**: `{brand}_{model_id}` (예: `bentz_0`)

브랜드와 모델을 **하나의 인덱스**에 `doc_type` 필드로 구분하여 저장합니다.

**브랜드 문서:**
```json
{ "doc_type": "brand", "name": "bentz" }
```

**모델 문서:**
```json
{
  "doc_type": "model",
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

---

## 공통 응답 형식

### 목록 응답
```json
{
  "apiVersion": "v1",
  "kind": "BrandList",
  "metadata": { "total": 2, "page": 1, "size": 10 },
  "items": [{ "name": "bentz" }, { "name": "bmw" }]
}
```

### 단일 항목 응답
```json
{
  "apiVersion": "v1",
  "kind": "Brand",
  "metadata": { "name": "bentz", "total": 1 },
  "data": { "models_count": 1 }
}
```

### 에러 응답
```json
{
  "apiVersion": "v1",
  "kind": "Status",
  "status": "Failure",
  "message": "Brand bentz not found",
  "code": 404
}
```

---

## 엔드포인트

### 브랜드 관리

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/v1/brands/` | 브랜드 목록 (`?page=1&size=10`) |
| `POST` | `/api/v1/brands/` | 브랜드 생성 — body: `{"name": "bentz"}` |
| `GET` | `/api/v1/brands/{brand}` | 브랜드 조회 |
| `PUT` | `/api/v1/brands/{brand}` | 브랜드 이름 변경 — body: `{"name": "새이름"}` |
| `DELETE` | `/api/v1/brands/{brand}` | 브랜드 + 하위 모델 전체 삭제 |

### 모델 관리

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/v1/brands/{brand}/models` | 모델 목록 |
| `POST` | `/api/v1/brands/{brand}/models` | 모델 생성 |
| `GET` | `/api/v1/brands/{brand}/models/{id}` | 모델 조회 |
| `PUT` | `/api/v1/brands/{brand}/models/{id}` | 모델 수정 |
| `DELETE` | `/api/v1/brands/{brand}/models/{id}` | 모델 삭제 |

### 검색

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/v1/cars/search?q=키워드` | 전체 텍스트 검색 |

---

## 검색 기능

`GET /api/v1/cars/search?q=e-class`

`name`, `brand`, `fuel_type`, `engine_cylinder` 필드에서 동시에 검색합니다 (`multi_match` 쿼리).

**응답 예시 (200)**
```json
{
  "apiVersion": "v1",
  "kind": "CarList",
  "metadata": { "query": "e-class", "total": 1 },
  "items": [
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
  ]
}
```

**오류**
- `400` — 검색어(`q`) 누락

---

## 프론트엔드 UI

| URL | 설명 |
|-----|------|
| `GET /ui/` | 브랜드/모델 관리 페이지 |
| `GET /ui/search` | 검색 페이지 |

---

## 테스트 실행

```bash
cd 4_opensearch_cars_api
pytest app_test.py -v
# 15 passed
```

테스트는 `cars_test` 인덱스를 사용하며, 각 테스트 전후로 인덱스를 초기화합니다.

---

## 사용 흐름 예시

```bash
# 1. 브랜드 생성
curl -X POST http://127.0.0.1:5001/api/v1/brands/ \
  -H "Content-Type: application/json" \
  -d '{"name": "bentz"}'

# 2. 모델 추가
curl -X POST http://127.0.0.1:5001/api/v1/brands/bentz/models \
  -H "Content-Type: application/json" \
  -d '{"model_id":0,"name":"e-class","price":1000000,"fuel_type":"gasoline","fuel_efficiency":"9.1~13.2km/l","engine_power":"367hp","engine_cylinder":"I6"}'

# 3. 검색
curl "http://127.0.0.1:5001/api/v1/cars/search?q=e-class"

# 4. 브랜드 이름 변경
curl -X PUT http://127.0.0.1:5001/api/v1/brands/bentz \
  -H "Content-Type: application/json" \
  -d '{"name": "mercedes"}'

# 5. 브랜드 삭제
curl -X DELETE http://127.0.0.1:5001/api/v1/brands/mercedes
```
