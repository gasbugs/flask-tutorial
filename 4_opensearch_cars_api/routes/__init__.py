# K8s 스타일 응답 헬퍼 함수 모음
# 모든 라우트 파일에서 이 함수들을 공통으로 사용합니다

def k8s_list(kind, items, metadata=None):
    """K8s 목록 응답: apiVersion/kind/metadata/items 구조"""
    meta = metadata or {}
    meta.setdefault('total', len(items))
    return {"apiVersion": "v1", "kind": kind, "metadata": meta, "items": items}, 200


def k8s_item(kind, metadata, data):
    """K8s 단일 항목 응답: apiVersion/kind/metadata/data 구조"""
    return {"apiVersion": "v1", "kind": kind, "metadata": metadata, "data": data}, 200


def k8s_error(message, code):
    """K8s 에러 응답: kind=Status, status=Failure 구조"""
    return {
        "apiVersion": "v1",
        "kind": "Status",
        "status": "Failure",
        "message": message,
        "code": code
    }, code
