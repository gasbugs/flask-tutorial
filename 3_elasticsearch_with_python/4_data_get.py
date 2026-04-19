"""
Elasticsearch 특정 문서 조회 예제

ID를 알고 있을 때 특정 문서 한 건을 정확하게 가져오는 방법입니다.
검색(search)과 달리 ID로 직접 찾으므로 속도가 가장 빠릅니다.
"""
from elasticsearch import Elasticsearch  # Elasticsearch Python 클라이언트

# 로컬 Elasticsearch 서버에 연결합니다.
es = Elasticsearch(["http://127.0.0.1:9200"])

# 특정 문서를 ID로 조회합니다.
# index: 조회할 인덱스 이름
# id: 조회할 문서의 고유 ID (3_data_insert.py에서 "1"로 저장했습니다)
data = es.get(index="my_index", id=1)
print(data)  # _source 필드 안에 실제 저장된 데이터가 들어 있습니다.
