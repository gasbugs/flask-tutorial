# Fluent Bit Configuration

이 디렉토리는 OpenSearch로 로그를 수집하고 전송하기 위한 Fluent Bit 설정 파일을 포함하고 있습니다.

## 주요 파일
- `fluent-bit.conf`: 로그 입력(Input) 및 출력(Output)을 정의하는 메인 파이프라인 설정.
- `parsers.conf`: 수집된 로그 데이터를 정규화하기 위한 파서(Parser) 정의.
- `db/`: Fluent Bit의 파일 읽기 위치(Offset)를 저장하는 데이터베이스 디렉토리.

## 수집 대상
1. **Docker 컨테이너 로그**: `/var/lib/docker/containers/*/*.log` 경로의 JSON 로그를 수집합니다.
2. **System Syslog**: `/var/log/syslog` 파일을 직접 읽어 수집합니다 (RFC3164 포맷).

## 실행 방법
이 설정을 포함하여 클러스터를 띄우려면 최상위 디렉토리에서 다음 명령을 실행하세요:
```bash
docker-compose -f docker-compose-logging.yml up -d
```
