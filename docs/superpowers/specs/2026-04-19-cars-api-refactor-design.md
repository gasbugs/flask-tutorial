# 설계 문서: Cars API REST 표준화

**날짜:** 2026-04-19  
**대상 파일:** `2_cars_api/app.py`, `2_cars_api/app_test.py`  
**수강 대상:** Python 기초 지식 보유, 웹/API 입문자

---

## 목표

Flask 튜토리얼의 Cars API를 REST 표준에 가깝게 개선하되, 비전공자 학생이 이해할 수 있는 수준을 유지한다.

---

## 변경 범위

### 1. URL 구조 정리

- namespace 이름을 `ns_cars` → `cars`로 변경
- 기존 `/ns_cars/cars/...` → `/cars/...`로 단순화
- 중복된 경로 제거

### 2. 응답 형식 통일

- 모든 성공 응답: `{"message": "...", "data": ...}` + HTTP 상태코드
- 모든 에러 응답: `{"message": "설명"}` + HTTP 상태코드
- `abort()` 제거, `return` 으로 통일하여 코드 흐름 명확화
- `Response` 객체 직접 반환 방식 제거

**HTTP 상태코드 기준:**
| 상황 | 코드 |
|------|------|
| 조회 성공 | 200 |
| 생성 성공 | 201 |
| 삭제 성공 | 204 |
| 잘못된 요청 | 400 |
| 없는 리소스 | 404 |
| 중복 | 409 |

### 3. 테스트 격리 버그 수정

- `car_info`가 전역 변수라 테스트 간 상태가 공유되는 문제 수정
- `autouse=True` fixture로 매 테스트 전 `car_info.clear()` 실행
- 각 테스트가 독립적으로 선행 데이터를 직접 생성하도록 수정

### 4. 페이지네이션

- 적용 위치: `GET /cars` (전체 목록) 만
- 쿼리 파라미터: `?page=1&size=10` (기본값 각각 1, 10)
- 응답에 `page`, `size`, `total` 포함

### 5. 입력 검증

- `POST /cars/<brand>/<model_id>` 에서 필수 필드 누락 시 400 반환
- 누락된 필드 목록을 에러 메시지에 포함
- `@api.expect(car_data)` 는 유지 (Swagger 문서용)

---

## 변경하지 않는 것

- `1_hello_flask/` 전체 — 입문 예제이므로 유지
- `3_elasticsearch_with_python/` 전체
- `car_info` 딕셔너리 구조 (`{brand: {model_id: data}}`)
- flask-restx, Swagger UI 구조
- 미구현 PUT(브랜드 이름 변경)은 주석으로 명확히 "실습 과제"임을 표시

---

## 예상 결과

- `pytest` 실행 시 모든 테스트가 순서 무관하게 통과
- Swagger UI(`/`)에서 API 명세 확인 가능
- 학생이 코드를 읽으면서 REST 패턴을 자연스럽게 익힐 수 있음
