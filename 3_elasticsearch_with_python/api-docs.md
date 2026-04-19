# OpenSearch with Python 문서

Python에서 OpenSearch를 사용하는 방법을 순서대로 실습하는 예제 모음입니다.

> **OpenSearch란?** Elasticsearch에서 파생된 오픈소스 검색 엔진입니다. API가 Elasticsearch와 거의 동일하여 같은 방식으로 사용할 수 있습니다.

---

## 사전 준비

### 1. OpenSearch 서버 실행

```bash
cd opensearch-docker-compose
podman-compose up -d   # 또는 docker compose up -d
```

서버 준비 확인:
```bash
curl -sk https://127.0.0.1:9200 -u admin:'TeSt432!23$#'
# {"name":"opensearch-node1", ...} 가 출력되면 준비 완료
```

### 2. 접속 정보

| 항목 | 값 |
|------|----|
| 주소 | `https://127.0.0.1:9200` |
| 사용자명 | `admin` |
| 비밀번호 | `TeSt432!23$#` |

### 3. 클라이언트 연결 공통 코드

모든 예제 파일에서 아래 코드로 연결합니다.

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "127.0.0.1", "port": 9200}],
    http_auth=("admin", "TeSt432!23$#"),
    use_ssl=True,
    verify_certs=False,   # 개발용 자체 서명 인증서 검증 생략
    ssl_show_warn=False
)
```

---

## 핵심 개념

| 개념 | 관계형 DB 비유 | 설명 |
|------|---------------|------|
| 인덱스(index) | 테이블 | 관련된 문서의 모음 |
| 문서(document) | 행(row) | JSON 형태의 데이터 단위 |
| 필드(field) | 열(column) | 문서 안의 각 항목 |
| ID | 기본키(PK) | 문서를 식별하는 고유 번호 |

---

## 실습 파일 순서

파일은 반드시 아래 순서대로 실행해야 합니다.

```
1_connection.py    → 연결 확인
2_index_list.py    → 인덱스 목록 조회
3_data_insert.py   → 데이터 삽입·수정·삭제
4_data_get.py      → 특정 문서 조회   (3번 실행 후)
5_data_search.py   → 검색 쿼리       (3번 실행 후)
```

---

## 파일별 상세 설명

### 1_connection.py — 연결 확인

OpenSearch 서버에 연결하고 클러스터 정보를 출력합니다.

```bash
python 1_connection.py
```

**출력 예시:**
```
{'name': 'opensearch-node1', 'cluster_name': 'opensearch-cluster', 'version': {'number': '3.x.x', ...}}
```

**사용 메서드:**

| 메서드 | 설명 |
|--------|------|
| `client.info()` | 서버 클러스터 정보를 반환합니다 |

---

### 2_index_list.py — 인덱스 목록 조회

서버에 존재하는 모든 인덱스 목록을 출력합니다. SQL의 `SHOW TABLES;` 와 같습니다.

```bash
python 2_index_list.py
```

**출력 예시:**
```
green open .opensearch-observability ...
green open my_index                  ...
```

**사용 메서드:**

| 메서드 | 설명 |
|--------|------|
| `client.cat.indices()` | 모든 인덱스 목록을 텍스트로 반환합니다 |

---

### 3_data_insert.py — 데이터 삽입·수정·삭제

문서를 삽입하고, 수정하고, 삭제하는 기본 CRUD 작업을 실습합니다.

```bash
python 3_data_insert.py
```

**실습 데이터:**
```python
doc = {"name": "Choi", "Job": "IT security"}
```

**사용 메서드:**

| 메서드 | SQL 비유 | 설명 |
|--------|----------|------|
| `client.index(index, id, body)` | `INSERT` | 문서를 삽입합니다. 같은 ID면 덮어씁니다 |
| `client.update(index, id, body)` | `UPDATE` | 지정한 필드만 부분 수정합니다 |
| `client.delete(index, id)` | `DELETE` | 문서 한 건을 삭제합니다 |

**update body 형식 주의:**
```python
# update는 {"doc": {수정할 필드}} 형태로 감싸야 합니다.
body = {"doc": {"name": "Jane Doe"}}
client.update(index="my_index", id="1", body=body)
```

**출력 예시:**
```
{'result': 'created', '_id': '1', ...}
{'result': 'updated', '_id': '1', ...}
{'result': 'deleted', '_id': '1', ...}
```

> ⚠️ 이 파일을 실행하면 마지막에 문서가 삭제됩니다. `4_data_get.py`와 `5_data_search.py`를 실행하려면 삭제 코드를 주석 처리하고 실행하세요.

---

### 4_data_get.py — 특정 문서 조회

ID를 이용해 특정 문서 한 건을 정확히 가져옵니다. 검색보다 속도가 빠릅니다.

> `3_data_insert.py`에서 문서를 삽입한 뒤 실행해야 합니다.

```bash
python 4_data_get.py
```

**사용 메서드:**

| 메서드 | SQL 비유 | 설명 |
|--------|----------|------|
| `client.get(index, id)` | `SELECT * WHERE id=1` | ID로 문서 한 건을 조회합니다 |

**출력 예시:**
```json
{
  "_index": "my_index",
  "_id": "1",
  "_source": { "name": "Choi", "Job": "IT security" }
}
```

결과에서 실제 데이터는 `_source` 필드 안에 있습니다.

---

### 5_data_search.py — 검색 쿼리

쿼리(query)를 사용해 조건에 맞는 문서를 검색합니다. OpenSearch의 핵심 기능입니다.

> `3_data_insert.py`에서 문서를 삽입한 뒤 실행해야 합니다.

```bash
python 5_data_search.py
```

**사용 메서드:**

| 메서드 | SQL 비유 | 설명 |
|--------|----------|------|
| `client.search(index, body)` | `SELECT * FROM ...` | 쿼리 조건으로 문서를 검색합니다 |

**match_all 쿼리 — 전체 조회:**
```python
body = {"query": {"match_all": {}}}
data = client.search(index="my_index", body=body)
```

**출력 구조:**
```json
{
  "hits": {
    "total": { "value": 1 },
    "hits": [
      { "_id": "1", "_source": { "name": "Choi", "Job": "IT security" } }
    ]
  }
}
```

검색 결과는 `hits.hits` 배열 안에 있으며, 각 항목의 `_source`에 실제 데이터가 들어 있습니다.

---

## 자주 쓰는 쿼리 패턴

```python
# 전체 문서 조회 (SQL: SELECT *)
{"query": {"match_all": {}}}

# 특정 필드로 검색 (SQL: WHERE name LIKE '%Choi%')
{"query": {"match": {"name": "Choi"}}}

# 정확히 일치하는 값 검색 (SQL: WHERE Job = 'IT security')
{"query": {"term": {"Job.keyword": "IT security"}}}
```
