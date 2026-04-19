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
