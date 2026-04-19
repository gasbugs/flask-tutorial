"""
OpenSearch 연결 예제

OpenSearch는 Elasticsearch에서 파생된 오픈소스 검색 엔진입니다.
API가 Elasticsearch와 거의 동일하여 같은 방식으로 사용할 수 있습니다.
이 파일은 Python에서 OpenSearch 서버에 연결하는 방법을 보여줍니다.

실행 전 OpenSearch 서버가 https://127.0.0.1:9200 에서 실행 중이어야 합니다.
"""
from opensearchpy import OpenSearch  # OpenSearch Python 클라이언트 라이브러리

# OpenSearch 서버에 연결합니다.
# use_ssl=True: HTTPS(암호화 통신)를 사용합니다.
# verify_certs=False: 개발 환경에서 자체 서명 인증서 검증을 생략합니다.
# ssl_show_warn=False: 인증서 관련 경고 메시지를 숨깁니다.
# http_auth: (사용자명, 비밀번호) 형태로 인증 정보를 전달합니다.
client = OpenSearch(
    hosts=[{"host": "127.0.0.1", "port": 9200}],
    http_auth=("admin", "TeSt432!23$#"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# 연결 확인: 서버 정보를 출력합니다. 연결에 성공하면 서버 정보가 출력됩니다.
print(client.info())
