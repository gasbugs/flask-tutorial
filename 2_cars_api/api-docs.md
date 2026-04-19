# Cars API 문서

자동차 정보를 관리하는 REST API입니다. 브랜드와 모델 계층 구조로 데이터를 관리합니다.

> **Swagger UI**: 서버 실행 후 `http://127.0.0.1:5000` 접속하면 이 문서의 내용을 웹 UI로 확인하고 직접 테스트할 수 있습니다.

---

## 서버 실행

```bash
python app.py
# http://127.0.0.1:5000 에서 실행됩니다.
```

---

## 데이터 구조

데이터는 메모리에 아래 형태로 저장됩니다. 서버를 재시작하면 초기화됩니다.

```
{
  "브랜드명": {
    모델ID(정수): {
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

**예시:**
```json
{
  "bentz": {
    "0": {
      "name": "e-class",
      "price": 1000000,
      "fuel_type": "gasoline",
      "fuel_efficiency": "9.1~13.2km/l",
      "engine_power": "367hp",
      "engine_cylinder": "I6"
    }
  }
}
```

---

## 공통 응답 형식

모든 응답은 JSON 형식입니다.

| 상황 | 상태코드 | 응답 예시 |
|------|----------|-----------|
| 조회 성공 | 200 | `{"message": "ok", "data": ...}` |
| 생성 성공 | 201 | `{"message": "created"}` |
| 삭제 성공 | 204 | (응답 본문 없음) |
| 잘못된 요청 | 400 | `{"message": "필수 항목이 누락되었습니다: ['name']"}` |
| 리소스 없음 | 404 | `{"message": "브랜드 bentz가 존재하지 않습니다"}` |
| 중복 | 409 | `{"message": "브랜드 bentz가 이미 존재합니다"}` |
| 미구현 | 501 | `{"message": "미구현 기능입니다"}` |

---

## 엔드포인트

### 전체 목록 조회

#### `GET /cars/`

등록된 모든 브랜드 목록을 페이지 단위로 조회합니다.

**쿼리 파라미터**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | 정수 | 1 | 페이지 번호 |
| `size` | 정수 | 10 | 페이지당 브랜드 수 |

**요청 예시**
```
GET /cars/?page=1&size=2
```

**응답 예시 (200)**
```json
{
  "message": "ok",
  "number_of_vehicles": 3,
  "total": 2,
  "page": 1,
  "size": 2,
  "car_info": {
    "bentz": { "0": { "name": "e-class", ... } },
    "bmw":   {}
  }
}
```

| 필드 | 설명 |
|------|------|
| `number_of_vehicles` | 전체 등록 차량 수 (모든 브랜드 합산) |
| `total` | 전체 브랜드 수 |
| `page` | 현재 페이지 번호 |
| `size` | 현재 페이지 크기 |
| `car_info` | 현재 페이지의 브랜드 데이터 |

---

### 브랜드 관리

#### `GET /cars/<brand>`

특정 브랜드의 차량 목록을 조회합니다.

**요청 예시**
```
GET /cars/bentz
```

**응답 예시 (200)**
```json
{
  "message": "ok",
  "number_of_vehicles": 1,
  "data": {
    "0": { "name": "e-class", "price": 1000000, ... }
  }
}
```

**오류**
- `404` — 브랜드가 존재하지 않을 때

---

#### `POST /cars/<brand>`

새로운 브랜드를 등록합니다. 요청 바디 없이 URL만으로 생성됩니다.

**요청 예시**
```
POST /cars/bentz
```

**응답 (201)**
```json
{ "message": "created" }
```

**오류**
- `409` — 브랜드가 이미 존재할 때

---

#### `DELETE /cars/<brand>`

브랜드와 해당 브랜드의 모든 모델을 삭제합니다.

**요청 예시**
```
DELETE /cars/bentz
```

**응답 (204)** — 응답 본문 없음

**오류**
- `404` — 브랜드가 존재하지 않을 때

---

#### `PUT /cars/<brand>`

> **실습 과제**: 브랜드 이름 변경 기능을 직접 구현해보세요.  
> 현재 `501 Not Implemented` 를 반환합니다.

---

### 모델 관리

#### `GET /cars/<brand>/<model_id>`

특정 브랜드의 특정 모델을 조회합니다.

**요청 예시**
```
GET /cars/bentz/0
```

**응답 예시 (200)**
```json
{
  "message": "ok",
  "model_id": 0,
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

**오류**
- `404` — 브랜드 또는 모델이 존재하지 않을 때

---

#### `POST /cars/<brand>/<model_id>`

특정 브랜드에 새 모델을 추가합니다.

**요청 바디 (JSON)**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | 문자열 | ✅ | 모델명 |
| `price` | 정수 | ✅ | 가격 |
| `fuel_type` | 문자열 | ✅ | 연료 종류 (예: gasoline, diesel, electric) |
| `fuel_efficiency` | 문자열 | ✅ | 연비 (예: 9.1~13.2km/l) |
| `engine_power` | 문자열 | ✅ | 엔진 출력 (예: 367hp) |
| `engine_cylinder` | 문자열 | ✅ | 실린더 구성 (예: I6, V8) |

**요청 예시**
```
POST /cars/bentz/0
Content-Type: application/json

{
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
{ "message": "created" }
```

**오류**
- `400` — 필수 필드 누락 (누락된 필드 목록 포함)
- `404` — 브랜드가 존재하지 않을 때
- `409` — 모델 ID가 이미 존재할 때

---

#### `PUT /cars/<brand>/<model_id>`

특정 모델의 정보를 수정합니다. 요청 바디의 모든 필드가 덮어쓰여집니다.

**요청 바디**: `POST`와 동일한 형식

**응답 (200)**
```json
{ "message": "ok" }
```

**오류**
- `404` — 브랜드 또는 모델이 존재하지 않을 때

---

#### `DELETE /cars/<brand>/<model_id>`

특정 모델을 삭제합니다.

**요청 예시**
```
DELETE /cars/bentz/0
```

**응답 (204)** — 응답 본문 없음

**오류**
- `404` — 브랜드 또는 모델이 존재하지 않을 때

---

## 사용 흐름 예시

```bash
# 1. 브랜드 생성
curl -X POST http://127.0.0.1:5000/cars/bentz

# 2. 모델 추가
curl -X POST http://127.0.0.1:5000/cars/bentz/0 \
  -H "Content-Type: application/json" \
  -d '{"name":"e-class","price":1000000,"fuel_type":"gasoline","fuel_efficiency":"9.1~13.2km/l","engine_power":"367hp","engine_cylinder":"I6"}'

# 3. 전체 목록 조회
curl http://127.0.0.1:5000/cars/

# 4. 특정 모델 조회
curl http://127.0.0.1:5000/cars/bentz/0

# 5. 모델 수정
curl -X PUT http://127.0.0.1:5000/cars/bentz/0 \
  -H "Content-Type: application/json" \
  -d '{"name":"e-class-updated","price":1100000,"fuel_type":"gasoline","fuel_efficiency":"10.0km/l","engine_power":"400hp","engine_cylinder":"I6"}'

# 6. 모델 삭제
curl -X DELETE http://127.0.0.1:5000/cars/bentz/0

# 7. 브랜드 삭제
curl -X DELETE http://127.0.0.1:5000/cars/bentz
```
