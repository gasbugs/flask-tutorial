# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask 튜토리얼 프로젝트로, 세 가지 주제 디렉터리로 구성된 학습용 코드베이스입니다.

## Running Code

### Flask 앱 실행
```bash
# 각 예제 파일 직접 실행
python 1_hello_flask/hello_flask.py
python 1_hello_flask/static_route.py
python 2_cars_api/app.py
```

### 테스트 실행
```bash
# 2_cars_api 전체 테스트
cd 2_cars_api && pytest

# 특정 테스트 파일
cd 2_cars_api && pytest app_test.py

# 단일 테스트 함수
cd 2_cars_api && pytest app_test.py::test_create_brand
```

## Architecture

### `1_hello_flask/`
기본 Flask 개념 예제들 (독립 실행 파일):
- `hello_flask.py` — 최소 Flask 앱
- `static_route.py` / `dynamic_route.py` — 라우팅 패턴
- `method_endpoint.py` — HTTP 메서드와 엔드포인트 이름 지정
- `template_rendering.py` — Jinja2 템플릿

### `2_cars_api/`
flask-restx 기반 REST API. `app.py`의 핵심 구조:
- `api.namespace('ns_cars')` 로 그룹화, 모든 URL은 `/ns_cars/` 접두사
- 데이터는 메모리 내 `car_info` 딕셔너리 (`{brand: {model_id: data}}`)
- 리소스 클래스: `Cars` → `CarsBrand` → `CarsBrandModel` 계층
- `@api.expect(car_data)` 데코레이터로 요청 바디 스키마 검증

테스트(`app_test.py`)는 pytest fixture `client`(`app.test_client()`)를 사용하며, 각 테스트는 격리된 인메모리 상태로 시작됩니다.

### `3_elasticsearch_with_python/`
Elasticsearch Python 클라이언트 예제 (순서대로 실행):
1. `1_connection.py` — ES 연결 (`https://127.0.0.1:9200`, `elastic`/`test1234`)
2. `2_index_list.py` → `3_data_insert.py` → `4_data_get.py` → `5_data_search.py`

ES 예제 실행 전 로컬 Elasticsearch 서버가 필요합니다 (포트 9200, `verify_certs=False`).
