"""
Elasticsearch 인덱스 목록 조회 예제

Elasticsearch에서 '인덱스(index)'는 데이터베이스의 '테이블'과 비슷한 개념입니다.
관련된 문서(데이터)를 하나의 인덱스로 묶어 관리합니다.
이 파일은 서버에 존재하는 모든 인덱스의 목록을 조회합니다.
"""
from elasticsearch import Elasticsearch  # Elasticsearch Python 클라이언트

# Elasticsearch 서버에 연결합니다.
# verify_certs=False: 개발용 자체 서명 인증서를 사용할 때 검증을 생략합니다.
es = Elasticsearch(["https://127.0.0.1:9200"],
                   verify_certs=False,
                   basic_auth=('elastic', 'test1234'))

# cat.indices()는 모든 인덱스 목록을 테이블 형태로 반환합니다.
# 데이터베이스의 'SHOW TABLES;' 명령과 비슷합니다.
data = es.cat.indices()
print(data)  # 인덱스 이름, 상태, 문서 수, 용량 등이 출력됩니다.
