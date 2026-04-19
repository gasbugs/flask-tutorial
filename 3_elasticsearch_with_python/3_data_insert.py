"""
Elasticsearch 데이터 삽입·수정·삭제 예제

Elasticsearch에서 데이터 한 건을 '문서(document)'라고 부릅니다.
문서는 JSON 형태로 저장되며, 각 문서는 고유한 ID를 가집니다.

이 파일에서는 문서 추가(index), 수정(update), 삭제(delete)를 순서대로 실습합니다.
"""
from elasticsearch import Elasticsearch  # Elasticsearch Python 클라이언트

# HTTP로 로컬 Elasticsearch에 연결합니다 (인증 없이 사용하는 기본 설정).
es = Elasticsearch(["http://127.0.0.1:9200"])

# 저장할 문서 데이터를 딕셔너리로 정의합니다.
doc = {
        "name": "Choi",
        "Job": "IT security"
}

# 문서를 삽입합니다.
# index: 저장할 인덱스 이름 ("my_index"가 없으면 자동으로 생성됩니다)
# id: 문서의 고유 ID. 같은 ID로 다시 삽입하면 덮어씌워집니다.
# document: 저장할 데이터
data = es.index(index="my_index", id="1", document=doc)
print(data)  # 삽입 결과 (result: "created" 또는 "updated")

# 문서를 부분 수정합니다.
# update는 지정한 필드만 변경하고 나머지 필드는 유지합니다.
document = {"name": "Jane Doe"}
data = es.update(index="my_index", id="1", doc=document)
print(data)  # 수정 결과 (result: "updated")

# 문서를 삭제합니다.
# index와 id로 특정 문서 한 건을 삭제합니다.
data = es.delete(index="my_index", id="1")
print(data)  # 삭제 결과 (result: "deleted")
