"""클라이언트 실행 설정

사용법:
    python main.py <machine_id>

머신 ID별 서버 배정:
    1, 2 → server1 (127.0.0.1:9000)
    3, 4 → server2 (127.0.0.1:9001)
    backup: 127.0.0.1:9002
"""
_PRIMARY_MAP = {
    1: ("127.0.0.1", 9000),
    2: ("127.0.0.1", 9000),
    3: ("127.0.0.1", 9001),
    4: ("127.0.0.1", 9001),
}

BACKUP_HOST: str = "127.0.0.1"
BACKUP_PORT: int = 9002


def _parse() -> int:
    import sys
    for arg in sys.argv[1:]:
        try:
            mid = int(arg)
            if mid in _PRIMARY_MAP:
                return mid
        except ValueError:
            continue
    return 1  # 테스트 환경 등 machine_id 미지정 시 기본값


MACHINE_ID: int = _parse()

SERVER_HOST: str = _PRIMARY_MAP[MACHINE_ID][0]
SERVER_PORT: int = _PRIMARY_MAP[MACHINE_ID][1]
