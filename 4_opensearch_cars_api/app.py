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
