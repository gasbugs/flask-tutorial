"""
Elasticsearch 연결 예제

Elasticsearch는 대용량 데이터를 빠르게 검색할 수 있는 검색 엔진입니다.
이 파일은 Python에서 Elasticsearch 서버에 연결하는 방법을 보여줍니다.

실행 전 Elasticsearch 서버가 https://127.0.0.1:9200 에서 실행 중이어야 합니다.
"""
from elasticsearch import Elasticsearch  # Elasticsearch Python 클라이언트 라이브러리

# Elasticsearch 서버에 연결합니다.
# verify_certs=False: HTTPS 인증서 검증을 생략합니다 (개발 환경에서 자체 서명 인증서 사용 시).
# basic_auth: (사용자명, 비밀번호) 형태로 인증 정보를 전달합니다.
es = Elasticsearch(["https://127.0.0.1:9200"],
                   verify_certs=False,
                   basic_auth=('elastic', 'test1234'))

# 연결 확인: 서버 정보를 출력합니다. 연결에 성공하면 서버 정보가 출력됩니다.
print(es.info())
