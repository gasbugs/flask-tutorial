"""
flask-restx 요청 스키마 정의 + OpenSearch 인덱스 매핑

flask-restx 스키마: Swagger UI에서 요청 형식을 자동으로 문서화합니다.
INDEX_MAPPING: OpenSearch가 각 필드를 어떻게 저장/검색할지 정의합니다.
"""
from flask_restx import fields

# 필수 차량 정보 필드 목록 — 이 필드가 없으면 400 에러를 반환합니다
REQUIRED_MODEL_FIELDS = ['name', 'price', 'fuel_type',
                          'fuel_efficiency', 'engine_power', 'engine_cylinder']

# OpenSearch 인덱스 매핑
# keyword: 정확한 일치 검색 (필터, 집계 등), text: 형태소 분석 후 전문 검색
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "doc_type":        {"type": "keyword"},
            "name":            {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "brand":           {"type": "keyword"},
            "model_id":        {"type": "keyword"},
            "price":           {"type": "integer"},
            "fuel_type":       {"type": "keyword"},
            "fuel_efficiency": {"type": "text"},
            "engine_power":    {"type": "keyword"},
            "engine_cylinder": {"type": "keyword"}
        }
    }
}


def get_schemas(api):
    """flask-restx API 요청 스키마를 생성하여 반환합니다."""
    brand_create = api.model('BrandCreate', {
        'name': fields.String(required=True, description='브랜드 이름 (예: bentz)')
    })
    brand_rename = api.model('BrandRename', {
        'name': fields.String(required=True, description='새 브랜드 이름')
    })
    model_create = api.model('ModelCreate', {
        'model_id':        fields.Integer(required=True, description='모델 ID (예: 0)'),
        'name':            fields.String(required=True,  description='모델명'),
        'price':           fields.Integer(required=True, description='가격'),
        'fuel_type':       fields.String(required=True,  description='연료 종류'),
        'fuel_efficiency': fields.String(required=True,  description='연비'),
        'engine_power':    fields.String(required=True,  description='엔진 출력'),
        'engine_cylinder': fields.String(required=True,  description='실린더 구성'),
    })
    model_update = api.model('ModelUpdate', {
        'name':            fields.String(required=True,  description='모델명'),
        'price':           fields.Integer(required=True, description='가격'),
        'fuel_type':       fields.String(required=True,  description='연료 종류'),
        'fuel_efficiency': fields.String(required=True,  description='연비'),
        'engine_power':    fields.String(required=True,  description='엔진 출력'),
        'engine_cylinder': fields.String(required=True,  description='실린더 구성'),
    })
    return brand_create, brand_rename, model_create, model_update
