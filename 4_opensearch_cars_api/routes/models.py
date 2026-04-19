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
            return k8s_item("Model",
                            {"brand": brand, "model_id": str(model_id)},
                            params)

        def delete(self, brand, model_id):
            """특정 모델을 삭제합니다."""
            if not client.brand_exists(brand):
                return k8s_error(f"Brand {brand} not found", 404)
            if not client.model_exists(brand, model_id):
                return k8s_error(
                    f"Model {model_id} not found in {brand}", 404)
            client.delete_model(brand, model_id)
            return '', 204
