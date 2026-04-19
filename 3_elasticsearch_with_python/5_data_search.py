"""
OpenSearch 검색 쿼리 예제

OpenSearch의 핵심 기능은 '검색'입니다.
다양한 쿼리(query)를 사용하여 조건에 맞는 문서를 빠르게 찾을 수 있습니다.

이 파일에서는 가장 기본적인 match_all 쿼리를 실습합니다.
match_all은 인덱스 안의 모든 문서를 반환합니다.
"""
from opensearchpy import OpenSearch  # OpenSearch Python 클라이언트

# OpenSearch 서버에 연결합니다.
client = OpenSearch(
    hosts=[{"host": "127.0.0.1", "port": 9200}],
    http_auth=("admin", "TeSt432!23$#"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# 검색 쿼리를 실행합니다.
# index: 검색할 인덱스 이름
# body: 검색 조건을 딕셔너리로 전달합니다.
#   match_all: {} → 조건 없이 전체 문서를 검색합니다. SQL의 'SELECT *'와 같습니다.
data = client.search(
    index="my_index",
    body={"query": {"match_all": {}}}
)

# 검색 결과는 hits.hits 배열 안에 있습니다.
# 각 항목의 _source 필드에 실제 문서 데이터가 들어 있습니다.
print(data)
