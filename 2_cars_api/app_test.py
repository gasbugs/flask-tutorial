# pylint: disable=redefined-outer-name
"""
pytest를 이용한 자동차 API 테스트 코드

pytest란 Python에서 가장 많이 쓰이는 테스트 프레임워크입니다.
터미널에서 'pytest' 명령어를 실행하면 test_로 시작하는 모든 함수를 자동으로 테스트합니다.
"""
import pytest
from app import app  # 테스트할 Flask 앱을 가져옵니다.

# API의 namespace 이름입니다. 모든 URL 앞에 붙습니다.
NS = 'cars'


# @pytest.fixture는 테스트 함수들이 공통으로 사용할 준비 코드를 정의합니다.
# 여기서는 실제 서버를 켜지 않고 가상의 클라이언트를 만들어 API를 테스트합니다.
@pytest.fixture
def client():
    """테스트용 가상 클라이언트를 생성합니다. 각 테스트 함수가 이 클라이언트를 받아 사용합니다."""
    with app.test_client() as test_client:
        yield test_client  # yield: 테스트 완료 후 자동으로 클라이언트를 정리합니다.


def test_get_root(client):
    """빈 상태에서 전체 목록 조회 시 차량 수 0, 빈 딕셔너리가 응답되는지 확인합니다."""
    response = client.get(f"/{NS}/")
    assert response.status == '200 OK'  # assert: 조건이 거짓이면 테스트 실패로 표시됩니다.
    assert response.json == {
            'number_of_vehicles': 0,
            'car_info': {}
    }


def test_create_brand(client):
    """브랜드(bentz)를 생성하고, 목록에 정상 반영되는지 확인합니다."""
    # 1단계: 브랜드 생성 요청 (POST)
    response = client.post(f"/{NS}/bentz", data={})
    assert response.status == '201 CREATED'  # 201: 생성 성공

    # 2단계: 생성 후 목록 조회로 결과를 검증합니다.
    response = client.get(f"/{NS}/")
    assert response.status == '200 OK'
    assert response.json == {'car_info': {'bentz': {}},
                             'number_of_vehicles': 0}


def test_create_model(client):
    """bentz 브랜드에 e-class 모델을 추가하고, 데이터가 올바르게 저장되는지 확인합니다."""
    # 추가할 차량 정보를 딕셔너리로 정의합니다.
    model = {
        "name": "e-class",
        "price": 1000000,
        "fuel_type": "gasoline",
        "fuel_efficiency": "9.1~13.2km/l",
        "engine_power": "367hp",
        "engine_cylinder": "I6"
    }

    # bentz 브랜드에 ID=0 모델을 추가합니다. json= 을 사용하면 자동으로 JSON 형식으로 전송됩니다.
    response = client.post(f"/{NS}/bentz/0",
                           json=model)
    assert response.status == '201 CREATED'

    # 추가 후 전체 목록 조회로 데이터 저장 여부를 검증합니다.
    response = client.get(f"/{NS}/")
    assert response.status == '200 OK'
    assert response.json == {'car_info': {'bentz': {'0': model}},
                             'number_of_vehicles': 1}
