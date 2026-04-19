"""
OpenSearch 연결 및 CRUD 담당 클라이언트

OpenSearch는 Elasticsearch에서 파생된 오픈소스 검색 엔진입니다.
이 클라이언트는 자동차 데이터를 저장/조회/검색하는 모든 메서드를 제공합니다.

데이터 구조:
  - 브랜드 문서: _id = "brand__{brand}", doc_type = "brand"
  - 모델 문서:   _id = "{brand}_{model_id}", doc_type = "model"
  두 종류의 문서를 하나의 인덱스에 doc_type 필드로 구분하여 저장합니다.
"""
from opensearchpy import OpenSearch, NotFoundError
from models import INDEX_MAPPING


class CarsClient:
    def __init__(self, index='cars'):
        # 사용할 인덱스 이름 (운영: 'cars', 테스트: 'cars_test')
        self.index = index
        # OpenSearch 서버에 연결합니다 (개발용 자체 서명 인증서 검증 생략)
        self._os = OpenSearch(
            hosts=[{"host": "127.0.0.1", "port": 9200}],
            http_auth=("admin", "TeSt432!23$#"),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )

    # ── 인덱스 관리 ─────────────────────────────────

    def create_index(self):
        """인덱스가 없으면 매핑 설정과 함께 생성합니다."""
        if not self._os.indices.exists(index=self.index):
            self._os.indices.create(index=self.index, body=INDEX_MAPPING)

    def delete_index(self):
        """인덱스와 모든 데이터를 삭제합니다 (테스트 초기화용)."""
        if self._os.indices.exists(index=self.index):
            self._os.indices.delete(index=self.index)

    # ── 내부 헬퍼 ───────────────────────────────────

    def _brand_doc_id(self, brand):
        """브랜드 문서의 고유 ID를 만듭니다. 예: 'brand__bentz'"""
        return f"brand__{brand}"

    def _model_doc_id(self, brand, model_id):
        """모델 문서의 고유 ID를 만듭니다. 예: 'bentz_0'"""
        return f"{brand}_{model_id}"

    # ── 브랜드 CRUD ──────────────────────────────────

    def get_brands(self, page=1, size=10):
        """브랜드 목록을 페이지 단위로 조회합니다. (brands, total) 튜플 반환"""
        body = {
            "query": {"term": {"doc_type": "brand"}},
            "from": (page - 1) * size,
            "size": size
        }
        result = self._os.search(index=self.index, body=body)
        hits = result['hits']
        total = hits['total']['value']
        brands = [hit['_source']['name'] for hit in hits['hits']]
        return brands, total

    def brand_exists(self, brand):
        """브랜드가 존재하는지 확인합니다."""
        return self._os.exists(index=self.index, id=self._brand_doc_id(brand))

    def create_brand(self, brand):
        """브랜드 문서를 생성합니다."""
        self._os.index(
            index=self.index,
            id=self._brand_doc_id(brand),
            body={"doc_type": "brand", "name": brand},
            refresh='wait_for'
        )

    def rename_brand(self, brand, new_name):
        """브랜드 이름을 변경합니다. 하위 모델 문서도 모두 새 브랜드로 이전됩니다."""
        self.create_brand(new_name)
        for model in self.get_models(brand):
            mid = model['model_id']
            data = {k: v for k, v in model.items()
                    if k not in ('doc_type', 'brand', 'model_id')}
            self.create_model(new_name, mid, data)
        self.delete_brand(brand)

    def delete_brand(self, brand):
        """브랜드 문서와 해당 브랜드의 모든 모델 문서를 삭제합니다."""
        self._os.delete(
            index=self.index,
            id=self._brand_doc_id(brand),
            refresh='wait_for'
        )
        self._os.delete_by_query(
            index=self.index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"doc_type": "model"}},
                            {"term": {"brand": brand}}
                        ]
                    }
                }
            },
            refresh=True
        )

    # ── 모델 CRUD ────────────────────────────────────

    def get_models(self, brand):
        """특정 브랜드의 모든 모델을 조회합니다. 모델 문서 리스트 반환"""
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"doc_type": "model"}},
                        {"term": {"brand": brand}}
                    ]
                }
            },
            "size": 1000
        }
        result = self._os.search(index=self.index, body=body)
        return [hit['_source'] for hit in result['hits']['hits']]

    def model_exists(self, brand, model_id):
        """모델이 존재하는지 확인합니다."""
        return self._os.exists(index=self.index,
                               id=self._model_doc_id(brand, str(model_id)))

    def get_model(self, brand, model_id):
        """특정 모델 문서를 조회합니다. 없으면 None 반환"""
        try:
            result = self._os.get(index=self.index,
                                  id=self._model_doc_id(brand, str(model_id)))
            return result['_source']
        except NotFoundError:
            return None

    def create_model(self, brand, model_id, data):
        """모델 문서를 생성합니다. data에는 name, price 등 차량 정보가 담깁니다."""
        doc = {
            "doc_type": "model",
            "brand": brand,
            "model_id": str(model_id),
            **data
        }
        self._os.index(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            body=doc,
            refresh='wait_for'
        )

    def update_model(self, brand, model_id, data):
        """모델 문서를 덮어씁니다 (전체 교체)."""
        doc = {
            "doc_type": "model",
            "brand": brand,
            "model_id": str(model_id),
            **data
        }
        self._os.index(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            body=doc,
            refresh='wait_for'
        )

    def delete_model(self, brand, model_id):
        """모델 문서를 삭제합니다."""
        self._os.delete(
            index=self.index,
            id=self._model_doc_id(brand, str(model_id)),
            refresh='wait_for'
        )

    # ── 검색 ─────────────────────────────────────────

    def search(self, q):
        """
        multi_match 쿼리로 모델 문서에서 전체 텍스트 검색을 수행합니다.
        name, brand, fuel_type, engine_cylinder 필드에서 동시에 검색합니다.
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"doc_type": "model"}},
                        {
                            "multi_match": {
                                "query": q,
                                "fields": ["name", "brand",
                                           "fuel_type", "engine_cylinder"]
                            }
                        }
                    ]
                }
            }
        }
        result = self._os.search(index=self.index, body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
