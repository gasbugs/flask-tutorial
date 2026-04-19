# Cars API REST 표준화 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `2_cars_api/app.py`의 Cars API를 REST 표준에 맞게 개선하고 테스트 격리 버그를 수정한다.

**Architecture:** 단일 파일 Flask 앱(`app.py`)을 유지하면서 namespace URL 정리, 응답 형식 통일, 페이지네이션, 입력 검증을 순차적으로 추가한다. 테스트(`app_test.py`)는 각 변경에 맞춰 함께 업데이트한다.

**Tech Stack:** Flask, flask-restx, pytest

---

## 파일 구조

| 파일 | 역할 |
|------|------|
| `2_cars_api/app.py` | Flask 앱 및 API 엔드포인트 (수정) |
| `2_cars_api/app_test.py` | pytest 테스트 (수정) |

---

## Task 1: URL 구조 정리 (namespace 변경)

**Files:**
- Modify: `2_cars_api/app.py`
- Modify: `2_cars_api/app_test.py`

### 목표
`/ns_cars/cars/...` → `/cars/...` 로 단순화

- [ ] **Step 1: 테스트의 NS 상수를 먼저 변경 (테스트가 실패해야 정상)**

`app_test.py` 상단 NS 변수를 수정합니다.

```python
# 변경 전
NS = 'ns_cars'

# 변경 후
NS = 'cars'
```

그리고 URL 패턴도 수정합니다. `/{NS}/cars` → `/{NS}` 로 변경합니다.

```python
def test_get_root(client):
    response = client.get(f"/{NS}")   # /ns_cars/cars → /cars
    ...

def test_create_brand(client):
    response = client.post(f"/{NS}/bentz", data={})   # /ns_cars/cars/bentz → /cars/bentz
    ...
    response = client.get(f"/{NS}")
    ...

def test_create_model(client):
    ...
    response = client.post(f"/{NS}/bentz/0", json=model)   # /ns_cars/cars/bentz/0 → /cars/bentz/0
    ...
    response = client.get(f"/{NS}")
    ...
```

- [ ] **Step 2: 테스트가 실패하는지 확인**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: FAILED (404 Not Found — 아직 URL 변경 안 됨)

- [ ] **Step 3: app.py namespace 및 라우트 변경**

```python
# 변경 전
ns_cars = api.namespace('ns_cars', description='Car APIs')

@ns_cars.route('/cars')
class Cars(Resource): ...

@ns_cars.route('/cars/<string:brand>')
class CarsBrand(Resource): ...

@ns_cars.route('/cars/<string:brand>/<int:model_id>')
class CarsBrandModel(Resource): ...
```

```python
# 변경 후
cars_ns = api.namespace('cars', description='Car APIs')

@cars_ns.route('/')
class Cars(Resource): ...

@cars_ns.route('/<string:brand>')
class CarsBrand(Resource): ...

@cars_ns.route('/<string:brand>/<int:model_id>')
class CarsBrandModel(Resource): ...
```

데코레이터 내부의 `ns_cars.` 도 모두 `cars_ns.` 으로 변경합니다 (예: `@api.expect(car_data)` 는 그대로 유지).

- [ ] **Step 4: 테스트 통과 확인**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: 3개 PASSED

- [ ] **Step 5: 커밋**

```bash
git add 2_cars_api/app.py 2_cars_api/app_test.py
git commit -m "refactor(cars-api): namespace ns_cars → cars, URL /ns_cars/cars → /cars

Feature: feat-001
Tests: passed
Progress: Task 1 완료 — URL 구조 정리"
```

---

## Task 2: 응답 형식 통일

**Files:**
- Modify: `2_cars_api/app.py`

### 목표
`abort()` 와 `Response` 객체를 모두 제거하고 `return dict, status_code` 형식으로 통일.

- [ ] **Step 1: app.py 전체 응답 형식 변경**

아래 전체 app.py 내용으로 교체합니다 (namespace는 Task 1에서 변경된 `cars_ns` 기준):

**Cars 클래스 (GET /cars):**
```python
def get(self):
    """등록된 모든 자동차 정보와 총 대수를 조회합니다."""
    count = sum(len(models) for models in car_info.values())
    return {
        'message': 'ok',
        'number_of_vehicles': count,
        'car_info': car_info
    }, 200
```

**CarsBrand 클래스:**
```python
def get(self, brand):
    """특정 브랜드의 차량 목록을 조회합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    return {
        'message': 'ok',
        'number_of_vehicles': len(car_info[brand]),
        'data': car_info[brand]
    }, 200

def post(self, brand):
    """새로운 브랜드를 등록합니다."""
    if brand in car_info:
        return {'message': f'브랜드 {brand}가 이미 존재합니다'}, 409
    car_info[brand] = dict()
    return {'message': 'created'}, 201

def delete(self, brand):
    """특정 브랜드와 모든 모델을 삭제합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    del car_info[brand]
    return '', 204

def put(self, brand):
    """브랜드 이름 변경 — 실습 과제: 이 메서드를 직접 구현해보세요."""
    # TODO(실습): new_name을 요청 바디에서 받아서 브랜드 이름을 바꾸는 기능을 구현하세요.
    return {'message': '미구현 기능입니다'}, 501
```

**CarsBrandModel 클래스:**
```python
def get(self, brand, model_id):
    """특정 브랜드의 특정 모델을 조회합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    if model_id not in car_info[brand]:
        return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404
    return {
        'message': 'ok',
        'model_id': model_id,
        'data': car_info[brand][model_id]
    }, 200

@api.expect(car_data)
def post(self, brand, model_id):
    """특정 브랜드에 새 모델을 추가합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    if model_id in car_info[brand]:
        return {'message': f'모델 ID {model_id}가 이미 존재합니다'}, 409
    params = request.get_json()
    car_info[brand][model_id] = params
    return {'message': 'created'}, 201

def delete(self, brand, model_id):
    """특정 모델을 삭제합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    if model_id not in car_info[brand]:
        return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404
    del car_info[brand][model_id]
    return '', 204

@api.expect(car_data)
def put(self, brand, model_id):
    """특정 모델의 정보를 수정합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    if model_id not in car_info[brand]:
        return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404
    params = request.get_json()
    car_info[brand][model_id] = params
    return {'message': 'ok'}, 200
```

- [ ] **Step 2: app_test.py 응답 검증 코드 업데이트**

응답 형식이 바뀌었으므로 기존 assert 도 수정합니다.

```python
def test_get_root(client):
    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 0
    assert data['car_info'] == {}


def test_create_brand(client):
    response = client.post(f"/{NS}/bentz", data={})
    assert response.status_code == 201

    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['car_info'] == {'bentz': {}}
    assert data['number_of_vehicles'] == 0


def test_create_model(client):
    model = {
        "name": "e-class",
        "price": 1000000,
        "fuel_type": "gasoline",
        "fuel_efficiency": "9.1~13.2km/l",
        "engine_power": "367hp",
        "engine_cylinder": "I6"
    }
    response = client.post(f"/{NS}/bentz/0", json=model)
    assert response.status_code == 201

    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 1
    assert data['car_info'] == {'bentz': {'0': model}}
```

- [ ] **Step 3: 테스트 통과 확인**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: 3개 PASSED

- [ ] **Step 4: 커밋**

```bash
git add 2_cars_api/app.py 2_cars_api/app_test.py
git commit -m "refactor(cars-api): 응답 형식 통일, abort() 제거, 한국어 에러 메시지

Feature: feat-001
Tests: passed
Progress: Task 2 완료 — 응답 형식 통일"
```

---

## Task 3: 테스트 격리 버그 수정

**Files:**
- Modify: `2_cars_api/app_test.py`
- Modify: `2_cars_api/app.py` (car_info import 추가)

### 목표
전역 `car_info` 딕셔너리를 매 테스트마다 초기화해서 테스트 간 상태 공유 제거.

- [ ] **Step 1: app_test.py 에 autouse fixture 추가 및 각 테스트 자급자족 구성**

`app_test.py` 파일 전체를 아래 내용으로 교체합니다:

```python
# pylint: disable=redefined-outer-name
"""
pytest를 이용한 자동차 API 테스트 코드

pytest란 Python에서 가장 많이 쓰이는 테스트 프레임워크입니다.
터미널에서 'pytest' 명령어를 실행하면 test_로 시작하는 모든 함수를 자동으로 테스트합니다.
"""
import pytest
from app import app, car_info  # car_info도 가져옵니다 — 테스트마다 초기화하기 위해서입니다.

# API의 namespace 이름입니다. 모든 URL 앞에 붙습니다.
NS = 'cars'


@pytest.fixture
def client():
    """테스트용 가상 클라이언트를 생성합니다."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_car_info():
    """매 테스트 실행 전에 car_info를 초기화합니다.
    autouse=True 이므로 모든 테스트 함수에 자동으로 적용됩니다.
    이 fixture가 없으면 앞선 테스트의 데이터가 다음 테스트에 남아 오염됩니다."""
    car_info.clear()
    yield
    car_info.clear()  # 테스트 종료 후에도 정리합니다.


def test_get_root(client):
    """빈 상태에서 전체 목록 조회 시 차량 수 0, 빈 딕셔너리가 응답되는지 확인합니다."""
    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 0
    assert data['car_info'] == {}


def test_create_brand(client):
    """브랜드(bentz)를 생성하고, 목록에 정상 반영되는지 확인합니다."""
    response = client.post(f"/{NS}/bentz", data={})
    assert response.status_code == 201

    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['car_info'] == {'bentz': {}}
    assert data['number_of_vehicles'] == 0


def test_create_model(client):
    """bentz 브랜드에 e-class 모델을 추가하고, 데이터가 올바르게 저장되는지 확인합니다."""
    # 이 테스트는 먼저 브랜드를 직접 만들고 시작합니다 — 다른 테스트에 의존하지 않습니다.
    client.post(f"/{NS}/bentz", data={})

    model = {
        "name": "e-class",
        "price": 1000000,
        "fuel_type": "gasoline",
        "fuel_efficiency": "9.1~13.2km/l",
        "engine_power": "367hp",
        "engine_cylinder": "I6"
    }

    response = client.post(f"/{NS}/bentz/0", json=model)
    assert response.status_code == 201

    response = client.get(f"/{NS}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 1
    assert data['car_info'] == {'bentz': {'0': model}}
```

- [ ] **Step 2: 테스트 순서를 역순으로 실행해서 격리 확인**

```bash
cd 2_cars_api && pytest app_test.py -v -p no:randomly
```

예상 결과: 3개 PASSED (순서 무관)

- [ ] **Step 3: 커밋**

```bash
git add 2_cars_api/app_test.py
git commit -m "fix(cars-api): 테스트 격리 버그 수정 — autouse fixture로 car_info 초기화

Feature: feat-001
Tests: passed
Progress: Task 3 완료 — 테스트 격리 버그 수정"
```

---

## Task 4: 페이지네이션

**Files:**
- Modify: `2_cars_api/app.py` (Cars.get 메서드)
- Modify: `2_cars_api/app_test.py` (테스트 추가)

### 목표
`GET /cars?page=1&size=2` 형태로 브랜드 목록을 나눠서 조회할 수 있게 한다.

- [ ] **Step 1: 페이지네이션 테스트 먼저 작성**

`app_test.py` 에 아래 테스트를 추가합니다:

```python
def test_pagination(client):
    """페이지네이션이 올바르게 동작하는지 확인합니다.
    브랜드 3개를 만들고 size=2 로 나눠서 조회합니다."""
    # 브랜드 3개 생성
    client.post(f"/{NS}/brand_a", data={})
    client.post(f"/{NS}/brand_b", data={})
    client.post(f"/{NS}/brand_c", data={})

    # 1페이지: brand_a, brand_b
    response = client.get(f"/{NS}?page=1&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 3       # 전체 브랜드 수
    assert data['page'] == 1
    assert data['size'] == 2
    assert len(data['car_info']) == 2  # 이번 페이지에 2개

    # 2페이지: brand_c
    response = client.get(f"/{NS}?page=2&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['car_info']) == 1  # 이번 페이지에 1개
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd 2_cars_api && pytest app_test.py::test_pagination -v
```

예상 결과: FAILED (응답에 `total`, `page`, `size` 없음)

- [ ] **Step 3: app.py Cars.get 메서드에 페이지네이션 추가**

```python
def get(self):
    """등록된 자동차 정보를 페이지 단위로 조회합니다.
    쿼리 파라미터: page(페이지 번호, 기본값 1), size(페이지당 항목 수, 기본값 10)
    예시: GET /cars?page=2&size=5"""
    # request.args.get: URL 뒤 ?key=value 형태의 값을 읽어옵니다.
    page = request.args.get('page', 1, type=int)   # 기본값: 1페이지
    size = request.args.get('size', 10, type=int)  # 기본값: 10개

    all_brands = list(car_info.keys())
    total = len(all_brands)

    # 슬라이싱으로 해당 페이지의 브랜드만 추출합니다.
    # 예: page=2, size=5 → [5:10]
    start = (page - 1) * size
    end = start + size
    paged_brands = all_brands[start:end]
    paged_info = {brand: car_info[brand] for brand in paged_brands}

    # 전체 차량 수는 페이지 관계없이 전체 기준으로 계산합니다.
    count = sum(len(models) for models in car_info.values())

    return {
        'message': 'ok',
        'number_of_vehicles': count,
        'total': total,        # 전체 브랜드 수
        'page': page,          # 현재 페이지
        'size': size,          # 페이지당 항목 수
        'car_info': paged_info
    }, 200
```

- [ ] **Step 4: 기존 테스트도 응답 구조에 맞게 업데이트**

`test_get_root`, `test_create_brand`, `test_create_model` 에서 `car_info` 와 `number_of_vehicles` 비교는 그대로 유지되지만, `total`/`page`/`size` 필드가 추가됩니다. 이미 있는 필드만 검사하므로 기존 테스트는 그대로 통과합니다.

- [ ] **Step 5: 전체 테스트 통과 확인**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: 4개 PASSED

- [ ] **Step 6: 커밋**

```bash
git add 2_cars_api/app.py 2_cars_api/app_test.py
git commit -m "feat(cars-api): GET /cars 페이지네이션 추가 (?page=1&size=10)

Feature: feat-001
Tests: passed
Progress: Task 4 완료 — 페이지네이션"
```

---

## Task 5: 입력 검증

**Files:**
- Modify: `2_cars_api/app.py` (CarsBrandModel.post 메서드)
- Modify: `2_cars_api/app_test.py` (테스트 추가)

### 목표
`POST /cars/<brand>/<model_id>` 요청 시 필수 필드가 누락되면 400 에러와 함께 누락된 필드 목록을 반환한다.

- [ ] **Step 1: 입력 검증 테스트 먼저 작성**

`app_test.py` 에 아래 테스트를 추가합니다:

```python
def test_create_model_missing_fields(client):
    """필수 필드가 누락된 요청 시 400 에러와 누락 필드 목록이 반환되는지 확인합니다."""
    client.post(f"/{NS}/bentz", data={})

    # name 과 price 를 빠뜨린 불완전한 요청
    incomplete_model = {
        "fuel_type": "gasoline",
        "fuel_efficiency": "9.1~13.2km/l",
        "engine_power": "367hp",
        "engine_cylinder": "I6"
    }

    response = client.post(f"/{NS}/bentz/0", json=incomplete_model)
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    # 누락된 필드 목록이 에러 메시지에 포함되어야 합니다.
    assert 'name' in data['message']
    assert 'price' in data['message']
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd 2_cars_api && pytest app_test.py::test_create_model_missing_fields -v
```

예상 결과: FAILED (현재 검증 없이 저장됨)

- [ ] **Step 3: app.py CarsBrandModel.post 에 검증 로직 추가**

```python
@api.expect(car_data)
def post(self, brand, model_id):
    """특정 브랜드에 새 모델을 추가합니다."""
    if brand not in car_info:
        return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
    if model_id in car_info[brand]:
        return {'message': f'모델 ID {model_id}가 이미 존재합니다'}, 409

    params = request.get_json()

    # 필수 필드 목록입니다. 하나라도 없으면 400 에러를 반환합니다.
    required_fields = ["name", "price", "fuel_type",
                       "fuel_efficiency", "engine_power", "engine_cylinder"]

    # 리스트 컴프리헨션: required_fields 중 params에 없는 것만 골라냅니다.
    missing = [field for field in required_fields if field not in params]
    if missing:
        return {'message': f'필수 항목이 누락되었습니다: {missing}'}, 400

    car_info[brand][model_id] = params
    return {'message': 'created'}, 201
```

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: 5개 PASSED

- [ ] **Step 5: 커밋**

```bash
git add 2_cars_api/app.py 2_cars_api/app_test.py
git commit -m "feat(cars-api): 모델 추가 시 필수 필드 검증 및 400 에러 반환

Feature: feat-001
Tests: passed
Progress: Task 5 완료 — 입력 검증, 전체 구현 완료"
```

---

## 최종 확인

- [ ] **전체 테스트 한 번 더 실행**

```bash
cd 2_cars_api && pytest app_test.py -v
```

예상 결과: 5개 PASSED

- [ ] **서버 직접 실행 후 Swagger UI 확인**

```bash
cd 2_cars_api && python app.py
# 브라우저에서 http://127.0.0.1:5000 접속 → API 문서 확인
```
