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
