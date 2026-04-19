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


def test_put_brand_not_implemented(client):
    """PUT 브랜드(이름 변경)는 미구현 기능으로 501이 반환되는지 확인합니다."""
    client.post(f"{NS}/", json={"name": "bentz"})
    response = client.put(f"{NS}/bentz", json={"name": "mercedes"})
    assert response.status_code == 501
    data = response.get_json()
    assert data['kind'] == 'Status'
    assert data['code'] == 501
