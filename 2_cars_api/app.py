"""
자동차 정보 REST API 예제 (flask-restx 사용)

REST API란 URL 주소와 HTTP 메서드(GET/POST/PUT/DELETE)를 조합하여
데이터를 주고받는 방식입니다.

flask-restx는 Flask를 확장하여 Swagger UI(API 명세서 웹페이지)를
자동으로 생성해주는 라이브러리입니다.
실행 후 http://127.0.0.1:5000 에 접속하면 API 문서를 확인할 수 있습니다.
"""
from flask import Flask, request  # Flask 기본 도구들 (Response, abort는 더 이상 사용하지 않습니다)
from flask_restx import Api, Resource, fields      # REST API 구성 도구들

# Flask 앱과 API 객체를 만듭니다.
app = Flask(__name__)
api = Api(app)  # Api 객체가 Swagger 문서를 자동 생성합니다.

# namespace(이름공간)는 관련된 API를 하나의 그룹으로 묶어주는 역할입니다.
# 모든 URL 앞에 '/cars'가 붙습니다. 예: /cars/bentz
cars_ns = api.namespace('cars', description='Car APIs')

# API가 받을 요청 데이터의 형태(스키마)를 정의합니다.
# 이 정의는 Swagger 문서에도 자동으로 표시됩니다.
car_data = api.model(
    'Car Data',
    {
      "name": fields.String(description="model name", required=True),       # 모델명 (필수)
      "price": fields.Integer(description="car price", required=True),      # 가격 (필수)
      "fuel_type": fields.String(description="fuel type", required=True),   # 연료 종류 (필수)
      "fuel_efficiency": fields.String(description="fuel efficiency",
                                       required=True),                       # 연비 (필수)
      "engine_power": fields.String(description="engine power", required=True),      # 엔진 출력 (필수)
      "engine_cylinder": fields.String(description="engine cylinder",
                                       required=True)                        # 실린더 수 (필수)
    }
)

# 자동차 데이터를 저장하는 메모리 딕셔너리입니다.
# 구조: { 브랜드명: { 모델ID: 모델데이터 } }
# 예: { "bentz": { 0: { "name": "e-class", ... } } }
# 서버를 재시작하면 데이터가 초기화됩니다(실제 서비스에서는 데이터베이스를 사용합니다).
car_info = {}


@cars_ns.route('/')
class Cars(Resource):
    """전체 자동차 목록을 관리하는 API 클래스입니다."""

    def get(self):
        """등록된 모든 자동차 정보와 총 대수를 조회합니다. (GET /cars)"""
        # 전체 차량 수를 계산합니다. (모든 브랜드의 모델 수 합산)
        count = sum(len(models) for models in car_info.values())

        # 응답 형식: dict와 HTTP 상태코드를 함께 반환합니다.
        return {
            'message': 'ok',
            'number_of_vehicles': count,  # 총 차량 수
            'car_info': car_info           # 전체 데이터
        }, 200


@cars_ns.route('/<string:brand>')
class CarsBrand(Resource):
    """특정 브랜드 정보를 관리하는 API 클래스입니다."""

    def get(self, brand):
        """특정 브랜드의 차량 목록을 조회합니다. (GET /cars/브랜드명)"""
        # 요청한 브랜드가 없으면 404 에러를 반환합니다.
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
        return {
            'message': 'ok',
            'number_of_vehicles': len(car_info[brand]),  # 해당 브랜드의 모델 수
            'data': car_info[brand]
        }, 200

    def post(self, brand):
        """새로운 브랜드를 등록합니다. (POST /cars/브랜드명)"""
        # 이미 존재하는 브랜드면 409(중복) 에러를 반환합니다.
        if brand in car_info:
            return {'message': f'브랜드 {brand}가 이미 존재합니다'}, 409

        # 새 브랜드를 빈 딕셔너리로 초기화합니다.
        car_info[brand] = dict()
        return {'message': 'created'}, 201  # 201: 생성 성공을 의미하는 HTTP 상태코드

    def delete(self, brand):
        """특정 브랜드와 해당 브랜드의 모든 모델을 삭제합니다. (DELETE /cars/브랜드명)"""
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404

        del car_info[brand]
        return '', 204  # 204: 삭제 성공 (응답 본문 없음)

    def put(self, brand):
        """브랜드 이름 변경 — 실습 과제: 이 메서드를 직접 구현해보세요."""
        # TODO(실습): new_name을 요청 바디에서 받아서 브랜드 이름을 바꾸는 기능을 구현하세요.
        return {'message': '미구현 기능입니다'}, 501


@cars_ns.route('/<string:brand>/<int:model_id>')
class CarsBrandModel(Resource):
    """특정 브랜드의 개별 모델을 관리하는 API 클래스입니다."""

    def get(self, brand, model_id):
        """특정 브랜드의 특정 모델을 조회합니다. (GET /cars/브랜드명/모델ID)"""
        # 브랜드가 없거나 모델이 없으면 404 에러를 반환합니다.
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
        if model_id not in car_info[brand]:
            return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404

        return {
            'message': 'ok',
            'model_id': model_id,
            'data': car_info[brand][model_id]
        }, 200

    @api.expect(car_data)  # 요청 바디가 car_data 스키마를 따라야 한다는 것을 Swagger에 표시합니다.
    def post(self, brand, model_id):
        """특정 브랜드에 새 모델을 추가합니다. (POST /cars/브랜드명/모델ID)"""
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
        if model_id in car_info[brand]:
            return {'message': f'모델 ID {model_id}가 이미 존재합니다'}, 409

        # 요청 바디(JSON)에서 차량 정보를 읽어 저장합니다.
        params = request.get_json()
        car_info[brand][model_id] = params

        return {'message': 'created'}, 201

    def delete(self, brand, model_id):
        """특정 모델을 삭제합니다. (DELETE /cars/브랜드명/모델ID)"""
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
        if model_id not in car_info[brand]:
            return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404

        del car_info[brand][model_id]

        return '', 204  # 204: 삭제 성공 (응답 본문 없음)

    @api.expect(car_data)
    def put(self, brand, model_id):
        """특정 모델의 정보를 수정합니다. (PUT /cars/브랜드명/모델ID)"""
        if brand not in car_info:
            return {'message': f'브랜드 {brand}가 존재하지 않습니다'}, 404
        if model_id not in car_info[brand]:
            return {'message': f'모델 ID {model_id}가 존재하지 않습니다'}, 404

        # 요청 바디에서 새 정보를 읽어 기존 데이터를 덮어씁니다.
        params = request.get_json()
        car_info[brand][model_id] = params

        return {'message': 'ok'}, 200


if __name__ == "__main__":
    # debug=True: 코드 수정 시 서버 자동 재시작. 개발 환경에서만 사용하세요.
    app.run(debug=True, host='0.0.0.0', port=5000)
