# 환경 설정 가이드

이 문서는 Flask 튜토리얼 프로젝트를 처음 실행하기 위한 환경 구성 방법을 안내합니다.

---

## 1. 가상환경(venv) 구성

가상환경은 프로젝트별로 패키지를 독립적으로 관리하는 Python 내장 기능입니다.
다른 프로젝트와 패키지 버전이 충돌하지 않도록 항상 가상환경을 사용하는 것을 권장합니다.

### 1-1. 가상환경 생성

```bash
# 프로젝트 루트 디렉터리에서 실행합니다.
python3 -m venv venv
```

### 1-2. 가상환경 활성화

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

활성화되면 터미널 프롬프트 앞에 `(venv)` 가 표시됩니다.

### 1-3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 1-4. 설치 확인

```bash
pip list
```

`flask`, `flask-restx`, `opensearch-py`, `pytest` 가 목록에 있으면 정상입니다.

### 가상환경 비활성화

```bash
deactivate
```

---

## 2. OpenSearch 실행 (Docker / Podman)

`3_elasticsearch_with_python` 예제를 실행하려면 OpenSearch 서버가 필요합니다.
`opensearch-docker-compose` 폴더의 Docker Compose 파일로 로컬에 간단하게 띄울 수 있습니다.

> Docker 대신 **Podman**을 사용해도 됩니다. 명령어가 동일합니다.

### 2-1. 사전 요구 사항

- Docker 또는 Podman 설치
- docker-compose 또는 podman-compose 설치

### 2-2. OpenSearch 클러스터 시작

```bash
cd opensearch-docker-compose
docker compose up -d        # Docker 사용 시
# 또는
podman-compose up -d        # Podman 사용 시
```

노드 3개 + 대시보드 컨테이너가 백그라운드로 실행됩니다.
처음 실행하면 이미지 다운로드로 수 분이 걸릴 수 있습니다.

### 2-3. 실행 확인

```bash
# 200 OK가 나오면 준비 완료입니다.
curl -sk https://127.0.0.1:9200 -u admin:'TeSt432!23$#' | python3 -m json.tool
```

### 2-4. 접속 정보

| 항목 | 값 |
|------|----|
| 주소 | `https://127.0.0.1:9200` |
| 사용자명 | `admin` |
| 비밀번호 | `TeSt432!23$#` |
| 대시보드 | `http://127.0.0.1:5601` |

### 2-5. OpenSearch 종료

```bash
cd opensearch-docker-compose
docker compose down         # Docker 사용 시
# 또는
podman-compose down         # Podman 사용 시
```

---

## 3. 테스트 실행

### Flask Cars API 테스트

```bash
# 가상환경 활성화 상태에서
cd 2_cars_api
pytest app_test.py -v
```

### OpenSearch 예제 실행 (순서대로)

OpenSearch가 실행 중인 상태에서 아래 파일을 순서대로 실행합니다.

```bash
cd 3_elasticsearch_with_python

python 1_connection.py   # 연결 확인
python 2_index_list.py   # 인덱스 목록 조회
python 3_data_insert.py  # 데이터 삽입·수정·삭제
python 4_data_get.py     # 특정 문서 조회 (3번 실행 후)
python 5_data_search.py  # 검색 쿼리 (3번 실행 후)
```

> `4_data_get.py`와 `5_data_search.py`는 `3_data_insert.py`에서 데이터를 삽입한 후 실행해야 합니다.
