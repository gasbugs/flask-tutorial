"""
pytest 기본 사용법 예제

pytest는 터미널에서 'pytest' 또는 'pytest 파일명.py' 로 실행합니다.
test_ 로 시작하는 함수를 자동으로 찾아 테스트합니다.
assert 조건이 참이면 PASSED, 거짓이면 FAILED로 표시됩니다.
"""


def test_func1():
    """0 == 0 은 참이므로 PASSED가 출력됩니다."""
    assert 0 == 0  # 0과 0은 같으므로 테스트 통과


def test_func2():
    """0 == 1 은 거짓이므로 FAILED가 출력됩니다. 의도적인 실패 예제입니다."""
    assert 0 == 1  # 0과 1은 다르므로 테스트 실패 → pytest가 어떻게 실패를 표시하는지 확인하세요.
