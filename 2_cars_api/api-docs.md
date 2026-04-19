# Cars API 문서 (K8s 스타일)

자동차 정보를 관리하는 REST API입니다. Kubernetes REST API 스타일을 따릅니다.

> **Swagger UI**: 서버 실행 후 `http://127.0.0.1:5000/docs` 접속하면 이 문서의 내용을 웹 UI로 확인하고 직접 테스트할 수 있습니다.

---

## 서버 실행

```bash
python app.py
# http://127.0.0.1:5000 에서 실행됩니다.
```

---

## K8s REST API 스타일이란?

이 API는 Kubernetes REST API 규칙을 따릅니다.

| 원칙 | 설명 |
|------|------|
| URL에 버전 포함 | `/api/v1/` 접두사 |
| 리소스 생성 시 이름을 body에 담음 | `POST /api/v1/brands/` + `{"name": "bentz"}` |
| 응답 구조 통일 | `apiVersion`, `kind`, `metadata`, `items`/`data` |
| 에러도 동일한 구조 | `kind: Status`, `status: Failure` |

---

## 데이터 구조

데이터는 메모리에 저장됩니다. 서버를 재시작하면 초기화됩니다.

```
{
  "브랜드명": {
    "모델ID문자열": {
      "name": "모델명",
      "price": 가격(정수),
      "fuel_type": "연료종류",
      "fuel_efficiency": "연비",
      "engine_power": "엔진출력",
      "engine_cylinder": "실린더"
    }
  }
}
```

---

## 공통 응답 형식

모든 응답은 JSON 형식입니다.

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
  "metadata": { "name": "bentz" },
  "data": { ... }
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

### HTTP 상태코드 기준

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

## 엔드포인트

### 브랜드 목록 조회

#### `GET /api/v1/brands/`

등록된 모든 브랜드 목록을 페이지 단위로 조회합니다.

**쿼리 파라미터**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | 정수 | 1 | 페이지 번호 |
| `size` | 정수 | 10 | 페이지당 브랜드 수 |

**응답 예시 (200)**
```json
{
  "apiVersion": "v1",
  "kind": "BrandList",
  "metadata": { "total": 2, "number_of_vehicles": 3, "page": 1, "size": 10 },
  "items": [{ "name": "bentz" }, { "name": "bmw" }]
}
```

---

### 브랜드 생성

#### `POST /api/v1/brands/`

새로운 브랜드를 등록합니다. 브랜드 이름을 요청 body에 담습니다.

**요청 body**
```json
{ "name": "bentz" }
```

**응답 (201)**
```json
{
  "apiVersion": "v1",
  "kind": "Brand",
  "metadata": { "name": "bentz" }
}
```

**오류**
- `400` — name 필드 누락
- `409` — 브랜드가 이미 존재할 때

---

### 브랜드 조회

#### `GET /api/v1/brands/{brand}`

특정 브랜드를 조회합니다.

**응답 예시 (200)**
```json
{
  "apiVersion": "v1",
  "kind": "Brand",
  "metadata": { "name": "bentz", "total": 1 },
  "data": { "0": { "name": "e-class", ... } }
}
```

**오류**
- `404` — 브랜드가 존재하지 않을 때

---

### 브랜드 이름 변경

#### `PUT /api/v1/brands/{brand}`

> **실습 과제**: 브랜드 이름 변경 기능을 직접 구현해보세요.
> 현재 `501 Not Implemented` 를 반환합니다.
>
> 힌트: body에서 `name`을 읽어 `car_info`의 키를 변경합니다.

---

### 브랜드 삭제

#### `DELETE /api/v1/brands/{brand}`

브랜드와 해당 브랜드의 모든 모델을 삭제합니다.

**응답 (204)** — 응답 본문 없음

**오류**
- `404` — 브랜드가 존재하지 않을 때

---

### 모델 목록 조회

#### `GET /api/v1/brands/{brand}/models`

특정 브랜드의 모델 목록을 조회합니다.

**응답 예시 (200)**
```json
{
  "apiVersion": "v1",
  "kind": "ModelList",
  "metadata": { "brand": "bentz", "total": 1 },
  "items": [{ "model_id": "0", "name": "e-class", ... }]
}
```

---

### 모델 생성

#### `POST /api/v1/brands/{brand}/models`

특정 브랜드에 새 모델을 추가합니다.

**요청 body**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `model_id` | 정수 | ✅ | 모델 ID |
| `name` | 문자열 | ✅ | 모델명 |
| `price` | 정수 | ✅ | 가격 |
| `fuel_type` | 문자열 | ✅ | 연료 종류 |
| `fuel_efficiency` | 문자열 | ✅ | 연비 |
| `engine_power` | 문자열 | ✅ | 엔진 출력 |
| `engine_cylinder` | 문자열 | ✅ | 실린더 구성 |

**요청 예시**
```json
{
  "model_id": 0,
  "name": "e-class",
  "price": 1000000,
  "fuel_type": "gasoline",
  "fuel_efficiency": "9.1~13.2km/l",
  "engine_power": "367hp",
  "engine_cylinder": "I6"
}
```

**응답 (201)**
```json
{
  "apiVersion": "v1",
  "kind": "Model",
  "metadata": { "brand": "bentz", "model_id": "0" }
}
```

**오류**
- `400` — 필수 필드 누락
- `404` — 브랜드가 존재하지 않을 때
- `409` — 모델 ID가 이미 존재할 때

---

### 모델 조회

#### `GET /api/v1/brands/{brand}/models/{model_id}`

특정 모델을 조회합니다.

**응답 예시 (200)**
```json
{
  "apiVersion": "v1",
  "kind": "Model",
  "metadata": { "brand": "bentz", "model_id": "0" },
  "data": {
    "name": "e-class",
    "price": 1000000,
    "fuel_type": "gasoline",
    "fuel_efficiency": "9.1~13.2km/l",
    "engine_power": "367hp",
    "engine_cylinder": "I6"
  }
}
```

---

### 모델 수정

#### `PUT /api/v1/brands/{brand}/models/{model_id}`

특정 모델의 정보를 수정합니다. 요청 body의 모든 필드가 덮어쓰여집니다.

**요청 body**: 모델 생성과 동일한 형식 (`model_id` 제외)

---

### 모델 삭제

#### `DELETE /api/v1/brands/{brand}/models/{model_id}`

특정 모델을 삭제합니다.

**응답 (204)** — 응답 본문 없음

---

## 사용 흐름 예시

```bash
# 1. 브랜드 생성
curl -X POST http://127.0.0.1:5000/api/v1/brands/ \
  -H "Content-Type: application/json" \
  -d '{"name": "bentz"}'

# 2. 모델 추가
curl -X POST http://127.0.0.1:5000/api/v1/brands/bentz/models \
  -H "Content-Type: application/json" \
  -d '{"model_id":0,"name":"e-class","price":1000000,"fuel_type":"gasoline","fuel_efficiency":"9.1~13.2km/l","engine_power":"367hp","engine_cylinder":"I6"}'

# 3. 브랜드 목록 조회
curl http://127.0.0.1:5000/api/v1/brands/

# 4. 특정 모델 조회
curl http://127.0.0.1:5000/api/v1/brands/bentz/models/0

# 5. 모델 수정
curl -X PUT http://127.0.0.1:5000/api/v1/brands/bentz/models/0 \
  -H "Content-Type: application/json" \
  -d '{"name":"e-class-updated","price":1100000,"fuel_type":"gasoline","fuel_efficiency":"10.0km/l","engine_power":"400hp","engine_cylinder":"I6"}'

# 6. 모델 삭제
curl -X DELETE http://127.0.0.1:5000/api/v1/brands/bentz/models/0

# 7. 브랜드 삭제
curl -X DELETE http://127.0.0.1:5000/api/v1/brands/bentz
```
