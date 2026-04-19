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
    response = client.get(f"/{NS}/")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 0
    assert data['car_info'] == {}


def test_create_brand(client):
    """브랜드(bentz)를 생성하고, 목록에 정상 반영되는지 확인합니다."""
    response = client.post(f"/{NS}/bentz", data={})
    assert response.status_code == 201

    response = client.get(f"/{NS}/")
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

    response = client.get(f"/{NS}/")
    assert response.status_code == 200
    data = response.get_json()
    assert data['number_of_vehicles'] == 1
    assert data['car_info'] == {'bentz': {'0': model}}


def test_pagination(client):
    """페이지네이션이 올바르게 동작하는지 확인합니다.
    브랜드 3개를 만들고 size=2 로 나눠서 조회합니다."""
    # 브랜드 3개 생성
    client.post(f"/{NS}/brand_a", data={})
    client.post(f"/{NS}/brand_b", data={})
    client.post(f"/{NS}/brand_c", data={})

    # 1페이지: brand_a, brand_b
    response = client.get(f"/{NS}/?page=1&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 3
    assert data['page'] == 1
    assert data['size'] == 2
    assert len(data['car_info']) == 2

    # 2페이지: brand_c
    response = client.get(f"/{NS}/?page=2&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['car_info']) == 1


def test_create_model_missing_fields(client):
    """필수 필드가 누락된 요청 시 400 에러와 누락 필드 목록이 반환되는지 확인합니다."""
    # 먼저 브랜드를 생성합니다.
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
    assert 'name' in data['message']
    assert 'price' in data['message']
