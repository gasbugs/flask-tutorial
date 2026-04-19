# Cars API K8s 스타일 리팩터링 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `2_cars_api/app.py`를 Kubernetes REST API 스타일로 리팩터링한다.

**Architecture:** 단일 파일 구조를 유지하면서 URL prefix `/api/v1/` 추가, 브랜드/모델 생성 시 이름을 body로 받도록 변경, 모든 응답을 K8s 표준 형식(`apiVersion`, `kind`, `metadata`, `items`)으로 통일한다.

**Tech Stack:** Flask, flask-restx, pytest

---

## 파일 구조

| 파일 | 변경 내용 |
|------|-----------|
| `2_cars_api/app.py` | 전체 리팩터링 |
| `2_cars_api/app_test.py` | URL/응답 형식 업데이트 |

---

## Task 1: 테스트 파일 전체 교체 (TDD — 먼저 실패하는 테스트 작성)

**Files:**
- Modify: `2_cars_api/app_test.py`

- [ ] **Step 1: app_test.py 전체를 아래 내용으로 교체**

```python
# pylint: disable=redefined-outer-name
"""
pytest를 이용한 자동차 API 테스트 코드 (K8s 스타일)

K8s REST API 스타일이란 URL에 버전(/api/v1/)이 포함되고,
응답이 apiVersion/kind/metadata/items 구조로 통일된 방식입니다.
"""
import pytest
from app import app, car_info

# 모든 API URL의 공통 prefix
NS = '/api/v1/brands'


@pytest.fixture
def client():
    """테스트용 가상 클라이언트를 생성합니다."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_car_info():
    """매 테스트 전후로 car_info를 초기화합니다."""
    car_info.clear()
    yield
    car_info.clear()


def test_get_brands_empty(client):
    """빈 상태에서 브랜드 목록 조회 시 K8s BrandList 형식으로 응답되는지 확인합니다."""
    response = client.get(f"{NS}/")
    assert response.status_code == 200
    data = response.get_json()
    assert data['apiVersion'] == 'v1'
    assert data['kind'] == 'BrandList'
    assert data['metadata']['total'] == 0
    assert data['items'] == []


def test_create_brand(client):
    """브랜드를 body의 name으로 생성하고 K8s Brand 형식으로 응답되는지 확인합니다."""
    response = client.post(f"{NS}/", json={"name": "bentz"})
    assert response.status_code == 201
    data = response.get_json()
    assert data['apiVersion'] == 'v1'
    assert data['kind'] == 'Brand'
    assert data['metadata']['name'] == 'bentz'


def test_create_brand_duplicate(client):
    """중복 브랜드 생성 시 K8s Status Failure 형식으로 409가 반환되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    response = client.post(f"{NS}/", json={"name": "bentz"})
    assert response.status_code == 409
    data = response.get_json()
    assert data['kind'] == 'Status'
    assert data['status'] == 'Failure'
    assert data['code'] == 409


def test_get_brand(client):
    """브랜드 생성 후 조회 시 K8s Brand 형식으로 응답되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    response = client.get(f"{NS}/bentz")
    assert response.status_code == 200
    data = response.get_json()
    assert data['kind'] == 'Brand'
    assert data['metadata']['name'] == 'bentz'


def test_get_brand_not_found(client):
    """존재하지 않는 브랜드 조회 시 K8s Status Failure 형식으로 404가 반환되는지 확인합니다."""
    response = client.get(f"{NS}/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert data['kind'] == 'Status'
    assert data['status'] == 'Failure'
    assert data['code'] == 404


def test_delete_brand(client):
    """브랜드 삭제 후 204가 반환되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    response = client.delete(f"{NS}/bentz")
    assert response.status_code == 204


def test_create_model(client):
    """모델을 body로 생성하고 K8s Model 형식으로 응답되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    model = {
        "model_id": 0,
        "name": "e-class",
        "price": 1000000,
        "fuel_type": "gasoline",
        "fuel_efficiency": "9.1~13.2km/l",
        "engine_power": "367hp",
        "engine_cylinder": "I6"
    }
    response = client.post(f"{NS}/bentz/models", json=model)
    assert response.status_code == 201
    data = response.get_json()
    assert data['apiVersion'] == 'v1'
    assert data['kind'] == 'Model'
    assert data['metadata']['brand'] == 'bentz'
    assert data['metadata']['model_id'] == '0'


def test_create_model_missing_fields(client):
    """필수 필드 누락 시 K8s Status Failure 형식으로 400이 반환되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    response = client.post(f"{NS}/bentz/models", json={"model_id": 0, "name": "e-class"})
    assert response.status_code == 400
    data = response.get_json()
    assert data['kind'] == 'Status'
    assert data['status'] == 'Failure'


def test_get_model(client):
    """모델 생성 후 조회 시 K8s Model 형식으로 응답되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    model = {"model_id": 0, "name": "e-class", "price": 1000000,
             "fuel_type": "gasoline", "fuel_efficiency": "9.1~13.2km/l",
             "engine_power": "367hp", "engine_cylinder": "I6"}
    client.post(f"{NS}/bentz/models", json=model)
    response = client.get(f"{NS}/bentz/models/0")
    assert response.status_code == 200
    data = response.get_json()
    assert data['kind'] == 'Model'
    assert data['data']['name'] == 'e-class'


def test_get_model_list(client):
    """모델 목록 조회 시 K8s ModelList 형식으로 응답되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    model = {"model_id": 0, "name": "e-class", "price": 1000000,
             "fuel_type": "gasoline", "fuel_efficiency": "9.1~13.2km/l",
             "engine_power": "367hp", "engine_cylinder": "I6"}
    client.post(f"{NS}/bentz/models", json=model)
    response = client.get(f"{NS}/bentz/models")
    assert response.status_code == 200
    data = response.get_json()
    assert data['kind'] == 'ModelList'
    assert data['metadata']['total'] == 1
    assert len(data['items']) == 1


def test_pagination(client):
    """페이지네이션 시 metadata에 total/page/size가 포함되는지 확인합니다."""
    for name in ['brand_a', 'brand_b', 'brand_c']:
        client.post(f"{NS}/", json={"name": name})
    response = client.get(f"{NS}/?page=1&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data['metadata']['total'] == 3
    assert data['metadata']['page'] == 1
    assert data['metadata']['size'] == 2
    assert len(data['items']) == 2
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd /Users/gasbugs/flask-tutorial/2_cars_api && ../venv/bin/pytest app_test.py -v 2>&1 | head -30
```

예상 결과: FAILED (URL 404 — 아직 구현 안 됨)

---

## Task 2: app.py 전체 교체 (K8s 스타일 구현)

**Files:**
- Modify: `2_cars_api/app.py`

- [ ] **Step 1: app.py 전체를 아래 내용으로 교체**

```python
"""
자동차 정보 REST API — Kubernetes 스타일 (K8s API 표준)

Kubernetes REST API 스타일의 핵심 원칙:
1. URL에 버전 포함: /api/v1/
2. 리소스 생성 시 이름을 URL이 아닌 body에 담음
3. 응답 형식 통일: apiVersion, kind, metadata, items/data
4. 에러도 동일한 형식: kind=Status, status=Failure
"""
from flask import Flask, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)
# prefix='/api/v1': 모든 URL 앞에 /api/v1이 자동으로 붙습니다.
api = Api(app, prefix='/api/v1', doc='/docs')

# namespace('brands'): 모든 URL 앞에 /brands가 추가로 붙습니다.
# 최종 URL 예시: /api/v1/brands/, /api/v1/brands/bentz
brands_ns = api.namespace('brands', description='Brand APIs')

# 브랜드 생성 요청 스키마 — 이름을 URL이 아닌 body로 받습니다 (K8s 스타일)
brand_create = api.model('BrandCreate', {
    "name": fields.String(required=True, description="브랜드 이름 (예: bentz)")
})

# 모델 생성 요청 스키마 — model_id도 body에 포함됩니다
model_create = api.model('ModelCreate', {
    "model_id": fields.Integer(required=True, description="모델 ID (예: 0)"),
    "name": fields.String(required=True, description="모델명"),
    "price": fields.Integer(required=True, description="가격"),
    "fuel_type": fields.String(required=True, description="연료 종류"),
    "fuel_efficiency": fields.String(required=True, description="연비"),
    "engine_power": fields.String(required=True, description="엔진 출력"),
    "engine_cylinder": fields.String(required=True, description="실린더")
})

# 모델 수정 요청 스키마 — model_id는 URL에 있으므로 body에서 제외
model_update = api.model('ModelUpdate', {
    "name": fields.String(required=True, description="모델명"),
    "price": fields.Integer(required=True, description="가격"),
    "fuel_type": fields.String(required=True, description="연료 종류"),
    "fuel_efficiency": fields.String(required=True, description="연비"),
    "engine_power": fields.String(required=True, description="엔진 출력"),
    "engine_cylinder": fields.String(required=True, description="실린더")
})

# 자동차 데이터를 저장하는 메모리 딕셔너리
# 구조: { 브랜드명: { "모델ID문자열": 모델데이터 } }
# 예: { "bentz": { "0": { "name": "e-class", ... } } }
car_info = {}


def k8s_list(kind, items, metadata=None):
    """K8s 스타일 목록 응답을 생성합니다.
    kind: 리소스 종류 (예: BrandList, ModelList)
    items: 목록 데이터
    metadata: 추가 정보 (total, page, size 등)"""
    meta = metadata or {}
    meta.setdefault('total', len(items))
    return {"apiVersion": "v1", "kind": kind, "metadata": meta, "items": items}, 200


def k8s_item(kind, metadata, data):
    """K8s 스타일 단일 항목 응답을 생성합니다."""
    return {"apiVersion": "v1", "kind": kind, "metadata": metadata, "data": data}, 200


def k8s_error(message, code):
    """K8s 스타일 에러 응답을 생성합니다.
    K8s에서 에러는 kind=Status, status=Failure 형태로 반환됩니다."""
    return {
        "apiVersion": "v1",
        "kind": "Status",
        "status": "Failure",
        "message": message,
        "code": code
    }, code


@brands_ns.route('/')
class BrandList(Resource):
    """브랜드 목록 조회 및 생성 (GET /api/v1/brands/, POST /api/v1/brands/)"""

    def get(self):
        """브랜드 목록을 페이지 단위로 조회합니다."""
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)

        all_brands = list(car_info.keys())
        total = len(all_brands)
        start = (page - 1) * size
        paged_brands = all_brands[start:start + size]
        count = sum(len(models) for models in car_info.values())

        # K8s items 형식: 각 브랜드를 {"name": "브랜드명"} 형태로 변환
        items = [{"name": b} for b in paged_brands]
        return k8s_list("BrandList", items, {
            "total": total,
            "number_of_vehicles": count,
            "page": page,
            "size": size
        })

    @brands_ns.expect(brand_create)
    def post(self):
        """새로운 브랜드를 생성합니다. body: {"name": "bentz"}"""
        params = request.get_json()
        name = params.get("name", "").strip()

        if not name:
            return k8s_error("name 필드가 필요합니다", 400)
        if name in car_info:
            return k8s_error(f"Brand {name} already exists", 409)

        car_info[name] = {}
        return {"apiVersion": "v1", "kind": "Brand",
                "metadata": {"name": name}}, 201


@brands_ns.route('/<string:brand>')
class BrandDetail(Resource):
    """특정 브랜드 조회, 수정, 삭제"""

    def get(self, brand):
        """특정 브랜드를 조회합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)
        return k8s_item("Brand",
                        {"name": brand, "total": len(car_info[brand])},
                        car_info[brand])

    def delete(self, brand):
        """브랜드와 모든 모델을 삭제합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)
        del car_info[brand]
        return '', 204

    def put(self, brand):
        """브랜드 이름 변경 — 실습 과제: 직접 구현해보세요.
        힌트: body에서 new_name을 읽어 car_info의 키를 변경합니다."""
        # TODO(실습): body의 name으로 브랜드 이름을 변경하는 기능을 구현하세요.
        return k8s_error("Not implemented", 501)


@brands_ns.route('/<string:brand>/models')
class ModelList(Resource):
    """특정 브랜드의 모델 목록 조회 및 생성"""

    def get(self, brand):
        """모델 목록을 조회합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)

        # model_id를 각 항목에 포함시켜서 반환합니다
        items = [{"model_id": k, **v} for k, v in car_info[brand].items()]
        return k8s_list("ModelList", items,
                        {"brand": brand, "total": len(items)})

    @brands_ns.expect(model_create)
    def post(self, brand):
        """새 모델을 추가합니다. body에 model_id와 차량 정보를 포함합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)

        params = request.get_json()
        model_id = params.get("model_id")

        if model_id is None:
            return k8s_error("model_id 필드가 필요합니다", 400)
        if str(model_id) in car_info[brand]:
            return k8s_error(f"Model {model_id} already exists in {brand}", 409)

        # 필수 필드 검증
        required = ["name", "price", "fuel_type",
                    "fuel_efficiency", "engine_power", "engine_cylinder"]
        missing = [f for f in required if f not in params]
        if missing:
            return k8s_error(f"필수 항목 누락: {missing}", 400)

        # model_id는 별도로 관리하므로 저장 데이터에서 제외합니다
        data = {k: v for k, v in params.items() if k != "model_id"}
        car_info[brand][str(model_id)] = data

        return {"apiVersion": "v1", "kind": "Model",
                "metadata": {"brand": brand, "model_id": str(model_id)}}, 201


@brands_ns.route('/<string:brand>/models/<int:model_id>')
class ModelDetail(Resource):
    """특정 모델 조회, 수정, 삭제"""

    def get(self, brand, model_id):
        """특정 모델을 조회합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)
        if str(model_id) not in car_info[brand]:
            return k8s_error(f"Model {model_id} not found in {brand}", 404)
        return k8s_item("Model",
                        {"brand": brand, "model_id": str(model_id)},
                        car_info[brand][str(model_id)])

    @brands_ns.expect(model_update)
    def put(self, brand, model_id):
        """모델 정보를 수정합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)
        if str(model_id) not in car_info[brand]:
            return k8s_error(f"Model {model_id} not found in {brand}", 404)
        params = request.get_json()
        car_info[brand][str(model_id)] = params
        return k8s_item("Model",
                        {"brand": brand, "model_id": str(model_id)},
                        params)

    def delete(self, brand, model_id):
        """특정 모델을 삭제합니다."""
        if brand not in car_info:
            return k8s_error(f"Brand {brand} not found", 404)
        if str(model_id) not in car_info[brand]:
            return k8s_error(f"Model {model_id} not found in {brand}", 404)
        del car_info[brand][str(model_id)]
        return '', 204


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
```

- [ ] **Step 2: 전체 테스트 통과 확인**

```bash
cd /Users/gasbugs/flask-tutorial/2_cars_api && ../venv/bin/pytest app_test.py -v
```

예상 결과: 12개 PASSED

- [ ] **Step 3: 커밋**

```bash
cd /Users/gasbugs/flask-tutorial
git add 2_cars_api/app.py 2_cars_api/app_test.py
git commit -m "refactor(cars-api): K8s REST API 스타일 적용

- URL prefix /api/v1/ 추가
- 브랜드/모델 생성 시 이름을 body로 받도록 변경
- 응답 형식 K8s 표준(apiVersion/kind/metadata/items) 통일
- 에러 응답 K8s Status 형식으로 통일
- 테스트 12개 추가

Feature: feat-001
Tests: passed
Progress: Sub-project 1 완료 — 2_cars_api K8s 리팩터링"
```

---

## 최종 확인

- [ ] **서버 실행 후 Swagger UI 확인**

```bash
cd /Users/gasbugs/flask-tutorial/2_cars_api && ../venv/bin/python app.py
# 브라우저에서 http://127.0.0.1:5000/docs 접속
```
