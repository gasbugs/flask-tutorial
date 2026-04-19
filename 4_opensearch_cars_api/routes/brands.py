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
