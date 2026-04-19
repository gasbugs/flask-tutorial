# 4_opensearch_cars_api 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `4_opensearch_cars_api/`를 신규 구현한다 — K8s REST API 스타일 + OpenSearch 백엔드 + 검색 + Jinja2 프론트엔드

**Architecture:** Flask app.py가 진입점이 되고, opensearch_client.py가 OpenSearch CRUD를 담당하며, routes/ 패키지에서 엔드포인트를 분리 정의한다. 브랜드는 `doc_type=brand` 문서로, 모델은 `doc_type=model` 문서로 같은 인덱스에 저장한다. 테스트는 `cars_test` 인덱스를 사용하고 매 테스트마다 인덱스를 초기화한다.

**Tech Stack:** Flask, flask-restx, opensearch-py, pytest, Jinja2

---

## 파일 구조

| 파일 | 역할 |
|------|------|
| `4_opensearch_cars_api/app.py` | Flask 앱 생성, API 네임스페이스 등록, UI 라우트 |
| `4_opensearch_cars_api/opensearch_client.py` | OpenSearch 연결 및 CRUD/검색 메서드 |
| `4_opensearch_cars_api/models.py` | flask-restx 스키마 정의 + INDEX_MAPPING + REQUIRED_MODEL_FIELDS |
| `4_opensearch_cars_api/routes/__init__.py` | k8s_list / k8s_item / k8s_error 헬퍼 함수 |
| `4_opensearch_cars_api/routes/brands.py` | GET/POST /api/v1/brands/, GET/PUT/DELETE /api/v1/brands/{brand} |
| `4_opensearch_cars_api/routes/models.py` | GET/POST /api/v1/brands/{brand}/models, GET/PUT/DELETE /api/v1/brands/{brand}/models/{id} |
| `4_opensearch_cars_api/routes/search.py` | GET /api/v1/cars/search?q= |
| `4_opensearch_cars_api/templates/base.html` | 공통 레이아웃 |
| `4_opensearch_cars_api/templates/index.html` | 브랜드/모델 관리 페이지 |
| `4_opensearch_cars_api/templates/search.html` | 검색 페이지 |
| `4_opensearch_cars_api/app_test.py` | pytest 통합 테스트 (cars_test 인덱스) |

---

## Task 1: 프로젝트 뼈대 생성

**Files:**
- Create: `4_opensearch_cars_api/app.py` (skeleton)
- Create: `4_opensearch_cars_api/opensearch_client.py` (skeleton)
- Create: `4_opensearch_cars_api/models.py` (skeleton)
- Create: `4_opensearch_cars_api/routes/__init__.py`
- Create: `4_opensearch_cars_api/routes/brands.py` (skeleton)
- Create: `4_opensearch_cars_api/routes/models.py` (skeleton)
- Create: `4_opensearch_cars_api/routes/search.py` (skeleton)

- [ ] **Step 1: 디렉터리 생성**

```bash
mkdir -p /Users/gasbugs/flask-tutorial/4_opensearch_cars_api/routes
mkdir -p /Users/gasbugs/flask-tutorial/4_opensearch_cars_api/templates
```

- [ ] **Step 2: 뼈대 파일 생성 — 임포트 오류 없이 테스트가 실행되도록**

`4_opensearch_cars_api/opensearch_client.py`:
```python
# OpenSearch 연결 및 CRUD를 담당합니다 — 구현 예정

class CarsClient:
    def __init__(self, index='cars'):
        self.index = index

    def create_index(self): pass
    def delete_index(self): pass
    def get_brands(self, page=1, size=10): return [], 0
    def brand_exists(self, brand): return False
    def create_brand(self, brand): pass
    def rename_brand(self, brand, new_name): pass
    def delete_brand(self, brand): pass
    def get_models(self, brand): return []
    def model_exists(self, brand, model_id): return False
    def get_model(self, brand, model_id): return None
    def create_model(self, brand, model_id, data): pass
    def update_model(self, brand, model_id, data): pass
    def delete_model(self, brand, model_id): pass
    def search(self, q): return []
```

`4_opensearch_cars_api/models.py`:
```python
# flask-restx 스키마 및 OpenSearch 인덱스 매핑 정의 — 구현 예정
from flask_restx import fields

REQUIRED_MODEL_FIELDS = ['name', 'price', 'fuel_type',
                          'fuel_efficiency', 'engine_power', 'engine_cylinder']

INDEX_MAPPING = {}

def get_schemas(api):
    brand_create = api.model('BrandCreate', {'name': fields.String(required=True)})
    brand_rename = api.model('BrandRename', {'name': fields.String(required=True)})
    model_create = api.model('ModelCreate', {
        'model_id': fields.Integer(required=True),
        'name': fields.String(required=True),
        'price': fields.Integer(required=True),
        'fuel_type': fields.String(required=True),
        'fuel_efficiency': fields.String(required=True),
        'engine_power': fields.String(required=True),
        'engine_cylinder': fields.String(required=True),
    })
    model_update = api.model('ModelUpdate', {
        'name': fields.String(required=True),
        'price': fields.Integer(required=True),
        'fuel_type': fields.String(required=True),
        'fuel_efficiency': fields.String(required=True),
        'engine_power': fields.String(required=True),
        'engine_cylinder': fields.String(required=True),
    })
    return brand_create, brand_rename, model_create, model_update
```

`4_opensearch_cars_api/routes/__init__.py`:
```python
# K8s 스타일 응답 헬퍼 함수 모음
# 모든 라우트 파일에서 이 함수들을 공통으로 사용합니다

def k8s_list(kind, items, metadata=None):
    """K8s 목록 응답: apiVersion/kind/metadata/items 구조"""
    meta = metadata or {}
    meta.setdefault('total', len(items))
    return {"apiVersion": "v1", "kind": kind, "metadata": meta, "items": items}, 200


def k8s_item(kind, metadata, data):
    """K8s 단일 항목 응답: apiVersion/kind/metadata/data 구조"""
    return {"apiVersion": "v1", "kind": kind, "metadata": metadata, "data": data}, 200


def k8s_error(message, code):
    """K8s 에러 응답: kind=Status, status=Failure 구조"""
    return {
        "apiVersion": "v1",
        "kind": "Status",
        "status": "Failure",
        "message": message,
        "code": code
    }, code
```

`4_opensearch_cars_api/routes/brands.py`:
```python
# 브랜드 API 라우트 — 구현 예정
from flask_restx import Resource
from flask import request
from routes import k8s_list, k8s_item, k8s_error


def register(ns, schemas, client):
    pass
```

`4_opensearch_cars_api/routes/models.py`:
```python
# 모델 API 라우트 — 구현 예정
from flask_restx import Resource
from flask import request
from routes import k8s_list, k8s_item, k8s_error


def register(ns, schemas, client):
    pass
```

`4_opensearch_cars_api/routes/search.py`:
```python
# 검색 API 라우트 — 구현 예정
from flask_restx import Resource
from flask import request
from routes import k8s_list


def register(ns, client):
    pass
```

`4_opensearch_cars_api/app.py`:
```python
# Flask 앱 진입점 — 구현 예정
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_restx import Api
from opensearch_client import CarsClient
from models import get_schemas
from routes.brands import register as register_brands
from routes.models import register as register_models
from routes.search import register as register_search

app = Flask(__name__)
api = Api(app, prefix='/api/v1', doc='/docs')

INDEX = os.environ.get('OPENSEARCH_INDEX', 'cars')
client = CarsClient(index=INDEX)

brands_ns = api.namespace('brands', description='Brand APIs')
cars_ns = api.namespace('cars', description='Cars Search API')

schemas = get_schemas(api)
register_brands(brands_ns, schemas, client)
register_models(brands_ns, schemas, client)
register_search(cars_ns, client)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## Task 2: app_test.py 작성 (TDD — 실패하는 테스트 먼저)

**Files:**
- Create: `4_opensearch_cars_api/app_test.py`

- [ ] **Step 1: app_test.py 작성**

```python
# pylint: disable=redefined-outer-name
"""
4_opensearch_cars_api 통합 테스트
OpenSearch cars_test 인덱스를 사용합니다. 각 테스트 전후로 인덱스를 초기화합니다.
"""
import os
os.environ['OPENSEARCH_INDEX'] = 'cars_test'

import pytest
from app import app, client as os_client

NS = '/api/v1/brands'
SEARCH_NS = '/api/v1/cars'


@pytest.fixture
def http():
    """테스트용 Flask HTTP 클라이언트를 생성합니다."""
    with app.test_client() as tc:
        yield tc


@pytest.fixture(autouse=True)
def clean_index():
    """각 테스트 전후로 cars_test 인덱스를 초기화합니다."""
    os_client.delete_index()
    os_client.create_index()
    yield
    os_client.delete_index()


# ── 브랜드 ─────────────────────────────────────────────

def test_get_brands_empty(http):
    """빈 상태에서 브랜드 목록 조회 시 BrandList 형식으로 응답됩니다."""
    r = http.get(f'{NS}/')
    assert r.status_code == 200
    d = r.get_json()
    assert d['apiVersion'] == 'v1'
    assert d['kind'] == 'BrandList'
    assert d['metadata']['total'] == 0
    assert d['items'] == []


def test_create_brand(http):
    """브랜드 생성 시 201과 Brand 형식으로 응답됩니다."""
    r = http.post(f'{NS}/', json={'name': 'bentz'})
    assert r.status_code == 201
    d = r.get_json()
    assert d['kind'] == 'Brand'
    assert d['metadata']['name'] == 'bentz'


def test_create_brand_duplicate(http):
    """중복 브랜드 생성 시 409 Status Failure 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.post(f'{NS}/', json={'name': 'bentz'})
    assert r.status_code == 409
    d = r.get_json()
    assert d['kind'] == 'Status'
    assert d['status'] == 'Failure'
    assert d['code'] == 409


def test_get_brand(http):
    """생성된 브랜드 조회 시 Brand 형식으로 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.get(f'{NS}/bentz')
    assert r.status_code == 200
    d = r.get_json()
    assert d['kind'] == 'Brand'
    assert d['metadata']['name'] == 'bentz'


def test_get_brand_not_found(http):
    """존재하지 않는 브랜드 조회 시 404 응답됩니다."""
    r = http.get(f'{NS}/nonexistent')
    assert r.status_code == 404
    d = r.get_json()
    assert d['kind'] == 'Status'
    assert d['code'] == 404


def test_delete_brand(http):
    """브랜드 삭제 시 204 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.delete(f'{NS}/bentz')
    assert r.status_code == 204


def test_rename_brand(http):
    """브랜드 이름 변경(PUT) 시 200 응답되고 old 브랜드는 404, new 브랜드는 200입니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.put(f'{NS}/bentz', json={'name': 'mercedes'})
    assert r.status_code == 200
    assert http.get(f'{NS}/bentz').status_code == 404
    assert http.get(f'{NS}/mercedes').status_code == 200


# ── 모델 ─────────────────────────────────────────────

MODEL_DATA = {
    'model_id': 0,
    'name': 'e-class',
    'price': 1000000,
    'fuel_type': 'gasoline',
    'fuel_efficiency': '9.1~13.2km/l',
    'engine_power': '367hp',
    'engine_cylinder': 'I6'
}


def test_create_model(http):
    """모델 생성 시 201과 Model 형식으로 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    assert r.status_code == 201
    d = r.get_json()
    assert d['kind'] == 'Model'
    assert d['metadata']['brand'] == 'bentz'
    assert d['metadata']['model_id'] == '0'


def test_create_model_missing_fields(http):
    """필수 필드 누락 시 400 Status Failure 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    r = http.post(f'{NS}/bentz/models', json={'model_id': 0, 'name': 'e-class'})
    assert r.status_code == 400
    d = r.get_json()
    assert d['kind'] == 'Status'
    assert d['status'] == 'Failure'


def test_get_model(http):
    """모델 조회 시 Model 형식으로 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    r = http.get(f'{NS}/bentz/models/0')
    assert r.status_code == 200
    d = r.get_json()
    assert d['kind'] == 'Model'
    assert d['data']['name'] == 'e-class'


def test_get_model_list(http):
    """모델 목록 조회 시 ModelList 형식으로 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    r = http.get(f'{NS}/bentz/models')
    assert r.status_code == 200
    d = r.get_json()
    assert d['kind'] == 'ModelList'
    assert d['metadata']['total'] == 1
    assert len(d['items']) == 1


def test_update_model(http):
    """모델 수정(PUT) 시 200과 수정된 Model 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    updated = {k: v for k, v in MODEL_DATA.items() if k != 'model_id'}
    updated['name'] = 's-class'
    r = http.put(f'{NS}/bentz/models/0', json=updated)
    assert r.status_code == 200
    d = r.get_json()
    assert d['data']['name'] == 's-class'


def test_delete_model(http):
    """모델 삭제 시 204 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    r = http.delete(f'{NS}/bentz/models/0')
    assert r.status_code == 204


# ── 검색 ─────────────────────────────────────────────

def test_search(http):
    """검색 시 CarList 형식으로 결과가 응답됩니다."""
    http.post(f'{NS}/', json={'name': 'bentz'})
    http.post(f'{NS}/bentz/models', json=MODEL_DATA)
    r = http.get(f'{SEARCH_NS}/search?q=e-class')
    assert r.status_code == 200
    d = r.get_json()
    assert d['kind'] == 'CarList'
    assert len(d['items']) >= 1


def test_search_empty(http):
    """검색어가 없으면 400 응답됩니다."""
    r = http.get(f'{SEARCH_NS}/search')
    assert r.status_code == 400
```

- [ ] **Step 2: 테스트 실행 — 실패 확인 (import는 성공해야 함)**

```bash
cd /Users/gasbugs/flask-tutorial/4_opensearch_cars_api && ../venv/bin/pytest app_test.py -v 2>&1 | head -40
```

예상 결과: 모든 테스트 FAILED (stub 반환값이 틀림) — ImportError는 없어야 함

---

## Task 3: opensearch_client.py 전체 구현

**Files:**
- Modify: `4_opensearch_cars_api/opensearch_client.py`

- [ ] **Step 1: opensearch_client.py 전체를 아래로 교체**

```python
"""
OpenSearch 연결 및 CRUD 담당 클라이언트

OpenSearch는 Elasticsearch에서 파생된 오픈소스 검색 엔진입니다.
이 클라이언트는 자동차 데이터를 저장/조회/검색하는 모든 메서드를 제공합니다.

데이터 구조:
  - 브랜드 문서: _id = "brand__{brand}", doc_type = "brand"
  - 모델 문서:   _id = "{brand}_{model_id}", doc_type = "model"
  두 종류의 문서를 하나의 인덱스에 doc_type 필드로 구분하여 저장합니다.
"""
from opensearchpy import OpenSearch, NotFoundError
from models import INDEX_MAPPING


class CarsClient:
    def __init__(self, index='cars'):
        # 사용할 인덱스 이름 (운영: 'cars', 테스트: 'cars_test')
        self.index = index
        # OpenSearch 서버에 연결합니다 (개발용 자체 서명 인증서 검증 생략)
        self._os = OpenSearch(
            hosts=[{"host": "127.0.0.1", "port": 9200}],
            http_auth=("admin", "TeSt432!23$#"),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )

    # ── 인덱스 관리 ─────────────────────────────────

    def create_index(self):
        """인덱스가 없으면 매핑 설정과 함께 생성합니다."""
        if not self._os.indices.exists(index=self.index):
            self._os.indices.create(index=self.index, body=INDEX_MAPPING)

    def delete_index(self):
        """인덱스와 모든 데이터를 삭제합니다 (테스트 초기화용)."""
        if self._os.indices.exists(index=self.index):
            self._os.indices.delete(index=self.index)

    # ── 내부 헬퍼 ───────────────────────────────────

    def _brand_doc_id(self, brand):
        """브랜드 문서의 고유 ID를 만듭니다. 예: 'brand__bentz'"""
        return f"brand__{brand}"

    def _model_doc_id(self, brand, model_id):
        """모델 문서의 고유 ID를 만듭니다. 예: 'bentz_0'"""
        return f"{brand}_{model_id}"

    # ── 브랜드 CRUD ──────────────────────────────────

    def get_brands(self, page=1, size=10):
        """브랜드 목록을 페이지 단위로 조회합니다. (brands, total) 튜플 반환"""
        body = {
            "query": {"term": {"doc_type": "brand"}},
            "from": (page - 1) * size,
            "size": size
        }
        result = self._os.search(index=self.index, body=body)
        hits = result['hits']
        total = hits['total']['value']
        brands = [hit['_source']['name'] for hit in hits['hits']]
        return brands, total

    def brand_exists(self, brand):
        """브랜드가 존재하는지 확인합니다."""
        return self._os.exists(index=self.index, id=self._brand_doc_id(brand))

    def create_brand(self, brand):
        """브랜드 문서를 생성합니다."""
        self._os.index(
            index=self.index,
            id=self._brand_doc_id(brand),
            body={"doc_type": "brand", "name": brand},
            refresh='wait_for'  # 즉시 검색 가능하도록 대기
        )

    def rename_brand(self, brand, new_name):
        """브랜드 이름을 변경합니다. 하위 모델 문서도 모두 새 브랜드로 이전됩니다."""
        # 새 브랜드 문서 생성
        self.create_brand(new_name)
        # 기존 모델을 새 브랜드로 복사
        for model in self.get_models(brand):
            mid = model['model_id']
            data = {k: v for k, v in model.items()
                    if k not in ('doc_type', 'brand', 'model_id')}
            self.create_model(new_name, mid, data)
        # 기존 브랜드와 모델 삭제
        self.delete_brand(brand)

    def delete_brand(self, brand):
        """브랜드 문서와 해당 브랜드의 모든 모델 문서를 삭제합니다."""
        # 브랜드 문서 삭제
        self._os.delete(
            index=self.index,
            id=self._brand_doc_id(brand),
            refresh='wait_for'
        )
        # 해당 브랜드의 모든 모델 문서 삭제
        self._os.delete_by_query(
            index=self.index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"doc_type": "model"}},
                            {"term": {"brand": brand}}
                        ]
                    }
                }
            },
            refresh=True
        )

    # ── 모델 CRUD ────────────────────────────────────

    def get_models(self, brand):
        """특정 브랜드의 모든 모델을 조회합니다. 모델 문서 리스트 반환"""
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"doc_type": "model"}},
                        {"term": {"brand": brand}}
                    ]
                }
            },
            "size": 1000
        }
        result = self._os.search(index=self.index, body=body)
        return [hit['_source'] for hit in result['hits']['hits']]

    def model_exists(self, brand, model_id):
        """모델이 존재하는지 확인합니다."""
        return self._os.exists(index=self.index,
                               id=self._model_doc_id(brand, str(model_id)))

    def get_model(self, brand, model_id):
        """특정 모델 문서를 조회합니다. 없으면 None 반환"""
        try:
            result = self._os.get(index=self.index,
                                  id=self._model_doc_id(brand, str(model_id)))
            return result['_source']
        except NotFoundError:
            return None

    def create_model(self, brand, model_id, data):
        """모델 문서를 생성합니다. data에는 name, price 등 차량 정보가 담깁니다."""
        doc = {
            "doc_type": "model",
            "brand": brand,
            "model_id": str(model_id),
            **data
        }
        self._os.index(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            body=doc,
            refresh='wait_for'
        )

    def update_model(self, brand, model_id, data):
        """모델 문서를 덮어씁니다 (전체 교체)."""
        doc = {
            "doc_type": "model",
            "brand": brand,
            "model_id": str(model_id),
            **data
        }
        self._os.index(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            body=doc,
            refresh='wait_for'
        )

    def delete_model(self, brand, model_id):
        """모델 문서를 삭제합니다."""
        self._os.delete(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            refresh='wait_for'
        )

    # ── 검색 ─────────────────────────────────────────

    def search(self, q):
        """
        multi_match 쿼리로 모델 문서에서 전체 텍스트 검색을 수행합니다.
        name, brand, fuel_type, engine_cylinder 필드에서 동시에 검색합니다.
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"doc_type": "model"}},
                        {
                            "multi_match": {
                                "query": q,
                                "fields": ["name", "brand",
                                           "fuel_type", "engine_cylinder"]
                            }
                        }
                    ]
                }
            }
        }
        result = self._os.search(index=self.index, body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
```

- [ ] **Step 2: 테스트 재실행 — 일부 통과 확인**

```bash
cd /Users/gasbugs/flask-tutorial/4_opensearch_cars_api && ../venv/bin/pytest app_test.py -v 2>&1 | head -50
```

예상 결과: routes가 아직 stub이라 대부분 실패, 하지만 client 자체 로직은 오류 없음

---

## Task 4: models.py 완성 + routes 구현

**Files:**
- Modify: `4_opensearch_cars_api/models.py`
- Modify: `4_opensearch_cars_api/routes/brands.py`
- Modify: `4_opensearch_cars_api/routes/models.py`
- Modify: `4_opensearch_cars_api/routes/search.py`

- [ ] **Step 1: models.py 완성**

```python
"""
flask-restx 요청 스키마 정의 + OpenSearch 인덱스 매핑

flask-restx 스키마: Swagger UI에서 요청 형식을 자동으로 문서화합니다.
INDEX_MAPPING: OpenSearch가 각 필드를 어떻게 저장/검색할지 정의합니다.
"""
from flask_restx import fields

# 필수 차량 정보 필드 목록 — 이 필드가 없으면 400 에러를 반환합니다
REQUIRED_MODEL_FIELDS = ['name', 'price', 'fuel_type',
                          'fuel_efficiency', 'engine_power', 'engine_cylinder']

# OpenSearch 인덱스 매핑
# keyword: 정확한 일치 검색 (필터, 집계 등), text: 형태소 분석 후 전문 검색
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "doc_type":        {"type": "keyword"},
            "name":            {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "brand":           {"type": "keyword"},
            "model_id":        {"type": "keyword"},
            "price":           {"type": "integer"},
            "fuel_type":       {"type": "keyword"},
            "fuel_efficiency": {"type": "text"},
            "engine_power":    {"type": "keyword"},
            "engine_cylinder": {"type": "keyword"}
        }
    }
}


def get_schemas(api):
    """flask-restx API 요청 스키마를 생성하여 반환합니다."""
    brand_create = api.model('BrandCreate', {
        'name': fields.String(required=True, description='브랜드 이름 (예: bentz)')
    })
    brand_rename = api.model('BrandRename', {
        'name': fields.String(required=True, description='새 브랜드 이름')
    })
    model_create = api.model('ModelCreate', {
        'model_id':        fields.Integer(required=True, description='모델 ID (예: 0)'),
        'name':            fields.String(required=True,  description='모델명'),
        'price':           fields.Integer(required=True, description='가격'),
        'fuel_type':       fields.String(required=True,  description='연료 종류'),
        'fuel_efficiency': fields.String(required=True,  description='연비'),
        'engine_power':    fields.String(required=True,  description='엔진 출력'),
        'engine_cylinder': fields.String(required=True,  description='실린더 구성'),
    })
    model_update = api.model('ModelUpdate', {
        'name':            fields.String(required=True,  description='모델명'),
        'price':           fields.Integer(required=True, description='가격'),
        'fuel_type':       fields.String(required=True,  description='연료 종류'),
        'fuel_efficiency': fields.String(required=True,  description='연비'),
        'engine_power':    fields.String(required=True,  description='엔진 출력'),
        'engine_cylinder': fields.String(required=True,  description='실린더 구성'),
    })
    return brand_create, brand_rename, model_create, model_update
```

- [ ] **Step 2: routes/brands.py 구현**

```python
"""
브랜드 CRUD 라우트
- GET  /api/v1/brands/        → 브랜드 목록 (페이지네이션)
- POST /api/v1/brands/        → 브랜드 생성 (body: {"name": "bentz"})
- GET  /api/v1/brands/{brand} → 브랜드 조회
- PUT  /api/v1/brands/{brand} → 브랜드 이름 변경 (body: {"name": "새이름"})
- DELETE /api/v1/brands/{brand} → 브랜드 삭제
"""
from flask import request
from flask_restx import Resource
from routes import k8s_list, k8s_item, k8s_error


def register(ns, schemas, client):
    """brands_ns 네임스페이스에 브랜드 라우트를 등록합니다."""
    brand_create, brand_rename, model_create, model_update = schemas

    @ns.route('/')
    class BrandList(Resource):
        """브랜드 목록 조회 및 생성"""

        def get(self):
            """브랜드 목록을 페이지 단위로 조회합니다."""
            page = request.args.get('page', 1, type=int)
            size = request.args.get('size', 10, type=int)
            brands, total = client.get_brands(page, size)
            items = [{"name": b} for b in brands]
            return k8s_list("BrandList", items,
                            {"total": total, "page": page, "size": size})

        @ns.expect(brand_create)
        def post(self):
            """새 브랜드를 생성합니다. 요청 body: {"name": "브랜드명"}"""
            params = request.get_json()
            name = (params.get("name") or "").strip()
            if not name:
                return k8s_error("name 필드가 필요합니다", 400)
            if client.brand_exists(name):
                return k8s_error(f"Brand {name} already exists", 409)
            client.create_brand(name)
            return {"apiVersion": "v1", "kind": "Brand",
                    "metadata": {"name": name}}, 201

    @ns.route('/<string:brand>')
    class BrandDetail(Resource):
        """특정 브랜드 조회 / 이름 변경 / 삭제"""

        def get(self, brand):
            """브랜드를 조회합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            models = client.get_models(brand)
            return k8s_item("Brand",
                            {"name": brand, "total": len(models)},
                            {"models_count": len(models)})

        @ns.expect(brand_rename)
        def put(self, brand):
            """브랜드 이름을 변경합니다. body: {"name": "새이름"}"""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            params = request.get_json()
            new_name = (params.get("name") or "").strip()
            if not new_name:
                return k8s_error("name 필드가 필요합니다", 400)
            if client.brand_exists(new_name):
                return k8s_error(f"Brand {new_name} already exists", 409)
            client.rename_brand(brand, new_name)
            return k8s_item("Brand", {"name": new_name}, {})

        def delete(self, brand):
            """브랜드와 모든 모델을 삭제합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            client.delete_brand(brand)
            return '', 204
```

- [ ] **Step 3: routes/models.py 구현**

```python
"""
모델 CRUD 라우트
- GET  /api/v1/brands/{brand}/models        → 모델 목록
- POST /api/v1/brands/{brand}/models        → 모델 생성
- GET  /api/v1/brands/{brand}/models/{id}  → 모델 조회
- PUT  /api/v1/brands/{brand}/models/{id}  → 모델 수정
- DELETE /api/v1/brands/{brand}/models/{id} → 모델 삭제

참고: 이 파일은 routes/models.py 입니다 (루트의 models.py와 다릅니다).
      루트의 models.py는 flask-restx 스키마를 정의하고,
      이 파일은 API 라우트 엔드포인트를 정의합니다.
"""
from flask import request
from flask_restx import Resource
from routes import k8s_list, k8s_item, k8s_error
from models import REQUIRED_MODEL_FIELDS


def register(ns, schemas, client):
    """brands_ns 네임스페이스에 모델 라우트를 등록합니다."""
    brand_create, brand_rename, model_create, model_update = schemas

    @ns.route('/<string:brand>/models')
    class ModelList(Resource):
        """특정 브랜드의 모델 목록 조회 및 생성"""

        def get(self, brand):
            """특정 브랜드의 모델 목록을 조회합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            raw_models = client.get_models(brand)
            # doc_type 내부 필드는 API 응답에서 제거합니다
            items = [{k: v for k, v in m.items() if k != 'doc_type'}
                     for m in raw_models]
            return k8s_list("ModelList", items, {"brand": brand})

        @ns.expect(model_create)
        def post(self, brand):
            """새 모델을 추가합니다. body에 model_id와 차량 정보를 포함합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            params = request.get_json()
            model_id = params.get("model_id")
            if model_id is None:
                return k8s_error("model_id 필드가 필요합니다", 400)
            if client.model_exists(brand, model_id):
                return k8s_error(
                    f"Model {model_id} already exists in {brand}", 409)
            missing = [f for f in REQUIRED_MODEL_FIELDS if f not in params]
            if missing:
                return k8s_error(f"필수 항목 누락: {missing}", 400)
            # model_id는 client가 별도로 관리하므로 data에서 제외합니다
            data = {k: v for k, v in params.items() if k != 'model_id'}
            client.create_model(brand, model_id, data)
            return {"apiVersion": "v1", "kind": "Model",
                    "metadata": {"brand": brand,
                                 "model_id": str(model_id)}}, 201

    @ns.route('/<string:brand>/models/<int:model_id>')
    class ModelDetail(Resource):
        """특정 모델 조회 / 수정 / 삭제"""

        def get(self, brand, model_id):
            """특정 모델을 조회합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            doc = client.get_model(brand, model_id)
            if doc is None:
                return k8s_error(
                    f"Model {model_id} not found in {brand}", 404)
            data = {k: v for k, v in doc.items()
                    if k not in ('doc_type', 'brand', 'model_id')}
            return k8s_item("Model",
                            {"brand": brand, "model_id": str(model_id)},
                            data)

        @ns.expect(model_update)
        def put(self, brand, model_id):
            """모델 정보를 전체 수정합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            if not client.model_exists(brand, model_id):
                return k8s_error(
                    f"Model {model_id} not found in {brand}", 404)
            params = request.get_json()
            client.update_model(brand, model_id, params)
            data = {k: v for k, v in params.items()}
            return k8s_item("Model",
                            {"brand": brand, "model_id": str(model_id)},
                            data)

        def delete(self, brand, model_id):
            """특정 모델을 삭제합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            if not client.model_exists(brand, model_id):
                return k8s_error(
                    f"Model {model_id} not found in {brand}", 404)
            client.delete_model(brand, model_id)
            return '', 204
```

- [ ] **Step 4: routes/search.py 구현**

```python
"""
검색 라우트
- GET /api/v1/cars/search?q=키워드 → multi_match 전체 텍스트 검색
"""
from flask import request
from flask_restx import Resource
from routes import k8s_list, k8s_error


def register(ns, client):
    """cars_ns 네임스페이스에 검색 라우트를 등록합니다."""

    @ns.route('/search')
    class CarSearch(Resource):
        """전체 텍스트 검색 — name, brand, fuel_type, engine_cylinder 필드 대상"""

        def get(self):
            """?q=키워드 로 차량을 검색합니다."""
            q = request.args.get('q', '').strip()
            if not q:
                return k8s_error("검색어(q)가 필요합니다", 400)
            results = client.search(q)
            # doc_type 내부 필드는 API 응답에서 제거합니다
            items = [{k: v for k, v in r.items() if k != 'doc_type'}
                     for r in results]
            return k8s_list("CarList", items, {"query": q})
```

---

## Task 5: app.py 완성

**Files:**
- Modify: `4_opensearch_cars_api/app.py`

- [ ] **Step 1: app.py 전체를 아래로 교체**

```python
"""
4_opensearch_cars_api — Flask 앱 진입점

OpenSearch를 백엔드로 사용하는 K8s 스타일 자동차 정보 API입니다.
- REST API: /api/v1/ (Swagger UI: /docs)
- 프론트엔드: /ui/ (Jinja2 서버 사이드 렌더링)

환경변수 OPENSEARCH_INDEX로 인덱스를 지정할 수 있습니다. 기본값: 'cars'
테스트 시 'cars_test'로 설정하여 운영 데이터와 격리합니다.
"""
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_restx import Api
from opensearch_client import CarsClient
from models import get_schemas
from routes.brands import register as register_brands
from routes.models import register as register_models
from routes.search import register as register_search

app = Flask(__name__)
# prefix='/api/v1': 모든 REST API URL 앞에 /api/v1이 붙습니다.
# doc='/docs': Swagger UI 주소
api = Api(app, prefix='/api/v1', doc='/docs',
          title='Cars API', description='K8s 스타일 자동차 정보 API')

# OPENSEARCH_INDEX 환경변수로 인덱스를 지정합니다 (테스트 격리에 사용)
INDEX = os.environ.get('OPENSEARCH_INDEX', 'cars')
client = CarsClient(index=INDEX)
client.create_index()

# 네임스페이스 등록 — URL 그룹을 나눕니다
brands_ns = api.namespace('brands', description='브랜드 CRUD API')
cars_ns = api.namespace('cars', description='차량 검색 API')

# 스키마 생성 및 라우트 등록
schemas = get_schemas(api)
register_brands(brands_ns, schemas, client)
register_models(brands_ns, schemas, client)
register_search(cars_ns, client)


# ── 프론트엔드 UI 라우트 ────────────────────────────────

@app.route('/ui/')
def ui_index():
    """메인 페이지: 브랜드 목록 + 선택된 브랜드의 모델 목록"""
    brand = request.args.get('brand')
    brands, _ = client.get_brands(size=100)
    models = client.get_models(brand) if brand else []
    # doc_type 필드는 템플릿에 노출하지 않습니다
    clean_models = [{k: v for k, v in m.items() if k != 'doc_type'}
                    for m in models]
    return render_template('index.html',
                           brands=brands,
                           selected_brand=brand,
                           models=clean_models)


@app.route('/ui/brands/create', methods=['POST'])
def ui_create_brand():
    """HTML 폼으로 브랜드를 생성합니다."""
    name = request.form.get('name', '').strip()
    if name and not client.brand_exists(name):
        client.create_brand(name)
    return redirect(url_for('ui_index', brand=name))


@app.route('/ui/brands/<brand>/models/create', methods=['POST'])
def ui_create_model(brand):
    """HTML 폼으로 모델을 추가합니다."""
    model_id = request.form.get('model_id', '0')
    data = {
        'name': request.form.get('name', ''),
        'price': int(request.form.get('price', 0) or 0),
        'fuel_type': request.form.get('fuel_type', ''),
        'fuel_efficiency': request.form.get('fuel_efficiency', ''),
        'engine_power': request.form.get('engine_power', ''),
        'engine_cylinder': request.form.get('engine_cylinder', ''),
    }
    if not client.model_exists(brand, model_id):
        client.create_model(brand, model_id, data)
    return redirect(url_for('ui_index', brand=brand))


@app.route('/ui/brands/<brand>/models/<model_id>/delete', methods=['POST'])
def ui_delete_model(brand, model_id):
    """HTML 폼으로 모델을 삭제합니다."""
    if client.model_exists(brand, model_id):
        client.delete_model(brand, model_id)
    return redirect(url_for('ui_index', brand=brand))


@app.route('/ui/search')
def ui_search():
    """검색 페이지: 검색어 입력 → 결과 테이블 표시"""
    q = request.args.get('q', '').strip()
    results = client.search(q) if q else []
    clean_results = [{k: v for k, v in r.items() if k != 'doc_type'}
                     for r in results]
    return render_template('search.html', q=q, results=clean_results)


if __name__ == '__main__':
    # 운영 서버는 포트 5001 사용 (2_cars_api가 5000 사용)
    app.run(debug=True, host='0.0.0.0', port=5001)
```

- [ ] **Step 2: 테스트 실행 — 모든 테스트 통과 확인**

```bash
cd /Users/gasbugs/flask-tutorial/4_opensearch_cars_api && ../venv/bin/pytest app_test.py -v
```

예상 결과: 15개 PASSED

---

## Task 6: 템플릿 구현

**Files:**
- Create: `4_opensearch_cars_api/templates/base.html`
- Create: `4_opensearch_cars_api/templates/index.html`
- Create: `4_opensearch_cars_api/templates/search.html`

- [ ] **Step 1: templates/base.html 작성**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Cars API{% endblock %}</title>
  <style>
    body { font-family: sans-serif; max-width: 960px; margin: 40px auto; padding: 0 16px; }
    nav { margin-bottom: 16px; }
    nav a { margin-right: 16px; text-decoration: none; color: #0055cc; }
    nav a:hover { text-decoration: underline; }
    hr { border: none; border-top: 1px solid #ddd; margin: 16px 0; }
    table { border-collapse: collapse; width: 100%; margin: 16px 0; }
    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th { background: #f5f5f5; }
    .brand-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
    .brand-btn { padding: 6px 14px; border: 1px solid #ccc;
                 border-radius: 4px; text-decoration: none; color: #333; }
    .brand-btn.active { background: #333; color: #fff; border-color: #333; }
    form.inline { display: inline; }
    .add-form { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; }
    .add-form input { padding: 5px 8px; border: 1px solid #ccc; border-radius: 3px; }
    .add-form button, button.small { padding: 5px 10px; cursor: pointer;
                                      border: 1px solid #999; border-radius: 3px; }
    .search-form { display: flex; gap: 8px; margin: 12px 0; }
    .search-form input[type=text] { flex: 1; padding: 7px; border: 1px solid #ccc;
                                     border-radius: 3px; font-size: 15px; }
    .search-form button { padding: 7px 16px; font-size: 15px; cursor: pointer; }
  </style>
</head>
<body>
  <nav>
    <a href="/ui/">브랜드 / 모델 관리</a>
    <a href="/ui/search">검색</a>
    <a href="/docs" target="_blank">Swagger API 문서</a>
  </nav>
  <hr>
  {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: templates/index.html 작성**

```html
{% extends 'base.html' %}
{% block title %}차량 관리{% endblock %}
{% block content %}
<h1>차량 관리</h1>

<h2>브랜드 목록</h2>
<div class="brand-list">
  {% for b in brands %}
    <a href="/ui/?brand={{ b }}"
       class="brand-btn {% if b == selected_brand %}active{% endif %}">{{ b }}</a>
  {% else %}
    <p>등록된 브랜드가 없습니다.</p>
  {% endfor %}
</div>

<form class="add-form" method="post" action="/ui/brands/create">
  <input type="text" name="name" placeholder="새 브랜드 이름" required>
  <button type="submit">브랜드 추가</button>
</form>

{% if selected_brand %}
<hr>
<h2>{{ selected_brand }} — 모델 목록</h2>

{% if models %}
<table>
  <tr>
    <th>ID</th><th>모델명</th><th>가격</th>
    <th>연료</th><th>연비</th><th>엔진출력</th><th>실린더</th><th>삭제</th>
  </tr>
  {% for m in models %}
  <tr>
    <td>{{ m.model_id }}</td>
    <td>{{ m.name }}</td>
    <td>{{ m.price | int | string }}원</td>
    <td>{{ m.fuel_type }}</td>
    <td>{{ m.fuel_efficiency }}</td>
    <td>{{ m.engine_power }}</td>
    <td>{{ m.engine_cylinder }}</td>
    <td>
      <form class="inline" method="post"
            action="/ui/brands/{{ selected_brand }}/models/{{ m.model_id }}/delete">
        <button class="small" type="submit">삭제</button>
      </form>
    </td>
  </tr>
  {% endfor %}
</table>
{% else %}
<p>등록된 모델이 없습니다.</p>
{% endif %}

<h3>모델 추가</h3>
<form class="add-form"
      method="post" action="/ui/brands/{{ selected_brand }}/models/create">
  <input type="number" name="model_id" placeholder="ID" required style="width:60px">
  <input type="text"   name="name"     placeholder="모델명" required>
  <input type="number" name="price"    placeholder="가격" required style="width:100px">
  <input type="text"   name="fuel_type"       placeholder="연료종류" required>
  <input type="text"   name="fuel_efficiency"  placeholder="연비" required>
  <input type="text"   name="engine_power"     placeholder="엔진출력" required>
  <input type="text"   name="engine_cylinder"  placeholder="실린더" required>
  <button type="submit">추가</button>
</form>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: templates/search.html 작성**

```html
{% extends 'base.html' %}
{% block title %}차량 검색{% endblock %}
{% block content %}
<h1>차량 검색</h1>
<p>모델명, 브랜드, 연료종류, 실린더 구성으로 검색할 수 있습니다.</p>

<form class="search-form" method="get" action="/ui/search">
  <input type="text" name="q" value="{{ q }}" placeholder="예: e-class, gasoline, I6" required>
  <button type="submit">검색</button>
</form>

{% if q %}
  {% if results %}
  <p><strong>{{ results | length }}건</strong> 검색됨 — 키워드: <em>{{ q }}</em></p>
  <table>
    <tr>
      <th>브랜드</th><th>ID</th><th>모델명</th><th>가격</th>
      <th>연료</th><th>연비</th><th>엔진출력</th><th>실린더</th>
    </tr>
    {% for r in results %}
    <tr>
      <td>{{ r.brand }}</td>
      <td>{{ r.model_id }}</td>
      <td>{{ r.name }}</td>
      <td>{{ r.price | int | string }}원</td>
      <td>{{ r.fuel_type }}</td>
      <td>{{ r.fuel_efficiency }}</td>
      <td>{{ r.engine_power }}</td>
      <td>{{ r.engine_cylinder }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p>검색 결과가 없습니다.</p>
  {% endif %}
{% endif %}
{% endblock %}
```

---

## Task 7: 전체 테스트 통과 확인 + 커밋

**Files:**
- Test: `4_opensearch_cars_api/app_test.py`

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd /Users/gasbugs/flask-tutorial/4_opensearch_cars_api && ../venv/bin/pytest app_test.py -v
```

예상 결과: 15개 PASSED

- [ ] **Step 2: 커밋**

```bash
cd /Users/gasbugs/flask-tutorial
git add 4_opensearch_cars_api/
git commit -m "feat(opensearch-cars-api): K8s 스타일 OpenSearch 자동차 API 신규 구현

- opensearch_client.py: OpenSearch CRUD + 검색 클라이언트
- routes/brands.py: 브랜드 CRUD (이름 변경 포함)
- routes/models.py: 모델 CRUD
- routes/search.py: multi_match 전체 텍스트 검색
- templates/: Jinja2 서버사이드 렌더링 UI
- app_test.py: 15개 통합 테스트 (cars_test 인덱스 격리)

Feature: feat-002
Tests: passed
Progress: Sub-project 2 완료 — 4_opensearch_cars_api 신규 구현"
```

---

## 최종 확인

- [ ] **서버 실행 후 UI 확인**

```bash
cd /Users/gasbugs/flask-tutorial/4_opensearch_cars_api && ../venv/bin/python app.py
# 브라우저에서:
#   http://127.0.0.1:5001/ui/       → 차량 관리 페이지
#   http://127.0.0.1:5001/ui/search → 검색 페이지
#   http://127.0.0.1:5001/docs      → Swagger UI
```
