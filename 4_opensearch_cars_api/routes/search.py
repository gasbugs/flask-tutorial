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
            items = [{k: v for k, v in r.items() if k != 'doc_type'}
                     for r in results]
            return k8s_list("CarList", items, {"query": q})
